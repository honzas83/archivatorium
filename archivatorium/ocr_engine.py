import logging
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, TypeAlias

import httpx
from ollama import Client
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

logger = logging.getLogger("archivatorium.ocr_engine")

SYSTEM_PROMPT = (
    "You are a highly accurate OCR and document analysis assistant.\n"
    "You extract text from technical document images while preserving the original structure, "
    "formatting, and logical hierarchy, maintaining the spatial relationships and visual layout of text elements.\n"
    "Your goal is to produce an output that faithfully retains:\n"
    "- Headings and subheadings\n"
    "- Paragraphs\n"
    "- Lists (ordered/unordered)\n"
    "- Tables (in Markdown or structured text format)\n"
    "- Page/section breaks, if applicable\n"
    "- Footnotes or annotations, if present\n"
    "- Figures and their associated captions (extract text from figures where legible)\n"
    "Do not summarize or rephrase the content.\n"
    "Avoid introducing content that is not clearly visible in the image.\n"
    "Empty output is likely incorrect unless the page is truly blank.\n"
    "Formatting rules:\n"
    "- Always concatenate the paragraph content on a single line without line breaks.\n"
    "- Separate paragraphs by one empty line when the document visually does so\n"
    "- Preserve indentation, bullet symbols, numbering, and whitespace\n"
    "- For tables, use Markdown pipe tables if clearly structured, otherwise fixed-width text blocks\n"
    "- Mark unreadable text as [unreadable]\n"
    "- Do not correct typos or normalize punctuation\n"
    "- Do not infer missing structure; only reproduce what is visible\n"
    "Avoid free interpretation; follow layout literally.\n"
)

USER_PROMPT = (
    "Extract the text content from this image of a document.\n"
    "Please preserve the spatial relationships and visual layout of text elements as closely as possible, including:\n"
    "- Section titles\n"
    "- Paragraph formatting\n"
    "- Bullet points and numbering\n"
    "- Tables\n"
    "This output will be post-processed to extract structured information, so accuracy and layout fidelity are essential."
)

GLM_USER_PROMPT = "Text Recognition:"

OllamaOptionValue: TypeAlias = int | float


@dataclass(frozen=True)
class OCRModeProfile:
    """Immutable request behavior selected independently from the model."""

    name: str
    system_prompt: str | None
    user_prompt: str
    include_previous_page_context: bool
    think: bool | None
    inference_defaults: tuple[tuple[str, OllamaOptionValue], ...]

    def default_options(self) -> dict[str, OllamaOptionValue]:
        return dict(self.inference_defaults)


@dataclass(frozen=True)
class InferenceOverrides:
    """Explicit runtime option overrides; ``None`` means not supplied."""

    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    repeat_penalty: float | None = None
    num_predict: int | None = None

    def __post_init__(self) -> None:
        if self.temperature is not None and self.temperature < 0:
            raise ValueError("temperature must be greater than or equal to 0")
        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")
        if self.top_k is not None and self.top_k < 0:
            raise ValueError("top_k must be greater than or equal to 0")
        if self.repeat_penalty is not None and self.repeat_penalty <= 0:
            raise ValueError("repeat_penalty must be greater than 0")
        if self.num_predict is not None and self.num_predict != -1 and self.num_predict < 1:
            raise ValueError("num_predict must be -1 or greater than or equal to 1")

    def explicit_options(self) -> dict[str, OllamaOptionValue]:
        return {
            name: value
            for name, value in (
                ("temperature", self.temperature),
                ("top_p", self.top_p),
                ("top_k", self.top_k),
                ("repeat_penalty", self.repeat_penalty),
                ("num_predict", self.num_predict),
            )
            if value is not None
        }


STANDARD_OCR_PROFILE = OCRModeProfile(
    name="standard",
    system_prompt=SYSTEM_PROMPT,
    user_prompt=USER_PROMPT,
    include_previous_page_context=True,
    think=None,
    inference_defaults=(("num_predict", 4096 * 4),),
)

GLM_OCR_PROFILE = OCRModeProfile(
    name="glm",
    system_prompt=None,
    user_prompt=GLM_USER_PROMPT,
    include_previous_page_context=False,
    think=False,
    inference_defaults=(
        ("temperature", 0.0),
        ("top_p", 0.00001),
        ("top_k", 1),
        ("repeat_penalty", 1.1),
        ("num_predict", 8192),
    ),
)


def resolve_ocr_mode(mode: str | None) -> OCRModeProfile:
    """Resolve the public mode, defaulting omitted values to standard OCR."""

    if mode is None or mode == "standard":
        return STANDARD_OCR_PROFILE
    if mode == "glm":
        return GLM_OCR_PROFILE
    raise ValueError(f"Unsupported OCR mode: {mode}")


class OCREngine:
    def __init__(
        self,
        host: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        model: str = "qwen3.5:9b",
        dpi: int = 300,
        mode: str = "standard",
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        repeat_penalty: float | None = None,
        num_predict: int | None = None,
    ):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.user = user or os.environ.get("OLLAMA_USER")
        self.password = password or os.environ.get("OLLAMA_PASSWORD")
        self.model = model
        self.dpi = dpi
        self.profile = resolve_ocr_mode(mode)
        self.mode = self.profile.name
        self.inference_overrides = InferenceOverrides(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repeat_penalty,
            num_predict=num_predict,
        )
        self.client = self._build_client()

    def _build_client(self) -> Client:
        timeout = httpx.Timeout(240.0)
        if self.user and self.password:
            logger.debug(
                "Building Ollama client with DigestAuth for host %s (timeout 240s)", self.host
            )
            auth = httpx.DigestAuth(self.user, self.password)
            return Client(host=self.host, auth=auth, timeout=timeout)
        return Client(host=self.host, timeout=timeout)

    def count_pdf_pages(self, pdf_path: Path) -> int:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            total = len(reader.pages)
        logger.info("PDF %s has %d pages", pdf_path, total)
        return total

    def render_pdf_page_to_png(self, pdf_path: Path, page_index_1based: int) -> Path:
        logger.info("Rendering PDF page %d at %d DPI", page_index_1based, self.dpi)
        images = convert_from_path(
            pdf_path=str(pdf_path),
            dpi=self.dpi,
            first_page=page_index_1based,
            last_page=page_index_1based,
            fmt="png",
            single_file=True,
        )
        if not images:
            raise RuntimeError(f"Failed to render page {page_index_1based} of {pdf_path}")
        image = images[0]

        tmp = tempfile.NamedTemporaryFile(
            prefix=f"ocr_page_{page_index_1based:04d}_", suffix=".png", delete=False
        )
        tmp_path = Path(tmp.name)
        tmp.close()
        image.save(tmp_path, format="PNG", optimize=True)
        logger.info("Saved temporary PNG %s", tmp_path)
        return tmp_path

    def ocr_single_page(
        self,
        image_path: Path,
        last_text: str = "",
        num_ctx: int = 8192,
        retry: int = 3,
        retry_backoff: float = 2.0,
    ) -> str:
        messages = self._build_messages(image_path, last_text)
        request_kwargs = self._build_chat_request(messages, num_ctx)

        last_err = None
        for attempt in range(1, retry + 1):
            try:
                logger.info("Calling Ollama (attempt %d) for image %s", attempt, image_path.name)
                resp = self.client.chat(**request_kwargs)
                # handle both dict and object response formats
                content = getattr(resp, "message", {}).get("content", "")
                if not content and isinstance(resp, dict):
                    content = resp.get("message", {}).get("content", "")
                logger.info("Received %d characters of OCR text from model", len(content or ""))
                return content or ""
            except Exception as e:
                last_err = e
                logger.warning("Ollama call failed on attempt %d: %s", attempt, e)
                if attempt < retry:
                    sleep_s = retry_backoff**attempt
                    logger.info("Retrying in %.1f s", sleep_s)
                    time.sleep(sleep_s)
                else:
                    logger.error("All retries exhausted for image %s", image_path)
                    raise
        if last_err:
            raise last_err
        return ""

    def _build_messages(self, image_path: Path, last_text: str) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        if self.profile.system_prompt is not None:
            messages.append({"role": "system", "content": self.profile.system_prompt})

        user_content = self.profile.user_prompt
        if self.profile.include_previous_page_context and last_text:
            user_content += f"\n\nFor OCR context, previous transcribed page was: {last_text}"
        messages.append(
            {
                "role": "user",
                "content": user_content,
                "images": [str(image_path)],
            }
        )
        return messages

    def _build_chat_request(self, messages: list[dict[str, Any]], num_ctx: int) -> dict[str, Any]:
        options = {"num_ctx": num_ctx, **self.profile.default_options()}
        options.update(self.inference_overrides.explicit_options())
        request: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "options": options,
            "stream": False,
        }
        if self.profile.think is not None:
            request["think"] = self.profile.think
        return request

    def run_ocr(
        self,
        input_pdf: Path,
        output_md: Optional[Path] = None,
        page_header: bool = True,
    ) -> str:
        from archivatorium.markdown_parser import MarkdownPageParser

        total_pages = self.count_pdf_pages(input_pdf)
        s = 1
        e = total_pages

        logger.info(
            "Starting OCR: %s, pages 1..%d of %d, DPI=%d, model=%s",
            input_pdf,
            total_pages,
            total_pages,
            self.dpi,
            self.model,
        )

        # 1) Parse existing pages if output_md exists
        existing_pages = {}
        if output_md and output_md.exists() and page_header:
            try:
                existing_content = output_md.read_text(encoding="utf-8")
                existing_pages = MarkdownPageParser.parse_pages(existing_content)
                logger.info("Parsed %d existing pages from %s", len(existing_pages), output_md.name)
            except Exception as ex:
                logger.warning("Failed to parse existing output %s: %s", output_md, ex)

        # 2) Process pages in the range
        all_pages = dict(existing_pages)
        last_text = ""

        for i in range(s, e + 1):
            # Check if this page is already successfully recognized
            existing_text = all_pages.get(i, "").strip()
            if existing_text:
                logger.info("Skipping page %d (already recognized)", i)
                last_text = existing_text
                continue

            logger.info("Processing page %d/%d", i - s + 1, e - s + 1)
            png_path = None
            try:
                png_path = self.render_pdf_page_to_png(input_pdf, i)
                # Context is the previous page's content
                context_text = ""
                if self.profile.include_previous_page_context:
                    context_text = last_text or all_pages.get(i - 1, "")
                text = self.ocr_single_page(
                    image_path=png_path,
                    last_text=context_text,
                    num_ctx=8192 * 3,
                )
                all_pages[i] = text.strip()
                last_text = text
            finally:
                if png_path and png_path.exists():
                    try:
                        png_path.unlink()
                        logger.debug("Removed temporary file %s", png_path)
                    except Exception as ex:
                        logger.warning("Failed to remove temporary file %s: %s", png_path, ex)

        # 3) Merge and sort all pages
        sorted_keys = sorted(all_pages.keys())
        chunks = []
        for k in sorted_keys:
            header = f"\n\n---\n\n# Page {k}\n\n" if page_header else "\n\n---\n\n"
            chunks.append(header + all_pages[k])

        merged = "".join(chunks).lstrip()
        if output_md:
            output_md.parent.mkdir(parents=True, exist_ok=True)
            output_md.write_text(merged, encoding="utf-8")
            logger.info("Saved output to %s", output_md)

        logger.info("OCR finished successfully")
        return merged
