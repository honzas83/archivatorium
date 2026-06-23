import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

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


class OCREngine:
    def __init__(
        self,
        host: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        model: str = "qwen3.5:9b",
        dpi: int = 300,
    ):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.user = user or os.environ.get("OLLAMA_USER")
        self.password = password or os.environ.get("OLLAMA_PASSWORD")
        self.model = model
        self.dpi = dpi
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
        from typing import Any

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT,
                "images": [str(image_path)],
            },
        ]
        if last_text:
            messages[-1]["content"] += (
                f"\n\nFor OCR context, previous transcribed page was: {last_text}"
            )

        last_err = None
        for attempt in range(1, retry + 1):
            try:
                logger.info("Calling Ollama (attempt %d) for image %s", attempt, image_path.name)
                resp = self.client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "num_ctx": num_ctx,
                        "num_predict": 4096 * 4,
                    },
                    stream=False,
                )
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
