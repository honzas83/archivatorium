import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from archivatorium.models.metadata import (
    AggregatedTaggingResult,
    MIN_SUBSTANTIVE_CONCEPTUAL_TAGS,
    SubstantiveWindowTaggingResult,
    TopicResult,
    WindowTaggingResult,
)
from archivatorium.services.flattening_service import FlatteningService
from archivatorium.services.ollama_client import OllamaClient
from archivatorium.services.windowing_service import SlidingWindowService
from archivatorium.utils.nlp import (
    estimate_tokens,
    filter_low_value_tags,
    normalize_tag_component,
    suppress_duplicates,
)

logger = logging.getLogger(__name__)


class TaggingQualityError(RuntimeError):
    """Raised when a substantive document receives an unacceptable tagging result."""


class TaggingService:
    """
    Service for extracting tiered tags (Entities, Topics, Conceptual)
    using a dynamic single-pass or sliding-window strategy.
    """

    def __init__(  # noqa: PLR0913
        self,
        ollama_client: OllamaClient,
        windowing_service: SlidingWindowService,
        themes_path: Path,
        useful_tags_path: Path | None = None,
        context_limit: int = 32000,
        model_name: str = "gemma4:31b",
    ):
        self.client = ollama_client
        self.windowing_service = windowing_service
        self.themes_path = themes_path
        self.useful_tags_path = useful_tags_path
        self.context_limit = context_limit
        self.model_name = model_name
        self.flattening_service = FlatteningService()

        # Load and Normalize Themes
        raw_themes = self._load_yaml(themes_path)
        self.themes = self._normalize_data(raw_themes)
        self.flattened_taxonomy = self.flattening_service.flatten(self.themes)
        self.taxonomy_prompt_text = yaml.dump(self.flattened_taxonomy, sort_keys=False)

        # Load and Normalize Useful Tags
        self.useful_tags = []
        if useful_tags_path:
            raw_tags = self._load_yaml(useful_tags_path).get("useful_tags", [])
            self.useful_tags = [normalize_tag_component(t) for t in raw_tags]
        self.useful_tags_prompt_text = ", ".join(self.useful_tags)

    def _normalize_data(self, data: Any) -> Any:
        """Recursively normalize categories and topics in the hierarchy."""
        if isinstance(data, list):
            return [self._normalize_data(item) for item in data]
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if k in ("category", "topic"):
                    new_dict[k] = normalize_tag_component(v)
                else:
                    new_dict[k] = self._normalize_data(v)
            return new_dict
        return data

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Failed to load YAML from {path}: {e}")
            return {}

    def extract_tags(
        self,
        text: str,
        reuse_hints: Any | None = None,
        source_filename: str | None = None,
    ) -> AggregatedTaggingResult:
        """
        Performs the second-pass tagging using a dynamic strategy.
        """
        tokens = estimate_tokens(text)
        is_substantive = self._is_substantive(text)
        protected_conceptual = self._protected_conceptual_terms(reuse_hints)

        if tokens <= self.context_limit:
            logger.debug(f"Using single pass for tagging ({tokens} tokens)")
            window_result = self._extract_chunk(
                text,
                require_conceptual_tags=is_substantive,
                reuse_hints=reuse_hints,
                source_filename=source_filename,
            )
            self._validate_conceptual_tags(
                window_result.conceptual_tags, is_substantive=is_substantive
            )

            # Normalize entities
            normalized_entities = []
            for entity in window_result.entity_tags:
                parts = entity.split("/")
                norm_parts = [normalize_tag_component(p) for p in parts]
                normalized_entities.append("/".join(norm_parts))
            entities_list = sorted(list(set(normalized_entities)))

            # Normalize topics and keep reasons
            topics_dict: dict[str, TopicResult] = {}
            for tr in window_result.topic_tags:
                parts = tr.topic.split("/")
                norm_parts = [normalize_tag_component(p) for p in parts]
                norm_topic = "/".join(norm_parts)
                if norm_topic not in topics_dict:
                    tr.topic = norm_topic
                    topics_dict[norm_topic] = tr

            topics_list = sorted(topics_dict.values(), key=lambda x: x.topic)
            topic_names = [t.topic for t in topics_list]

            # Normalize conceptual tags (take all generated by LLM)
            normalized_conceptual = [
                normalize_tag_component(t) for t in window_result.conceptual_tags
            ]

            # Apply filtering and suppression
            filtered_conceptual = filter_low_value_tags(normalized_conceptual)
            suppressed_conceptual = suppress_duplicates(
                filtered_conceptual,
                entities_list,
                topic_names,
                protected_terms=protected_conceptual,
            )
            self._validate_conceptual_tags(suppressed_conceptual, is_substantive=is_substantive)

            return AggregatedTaggingResult(
                conceptual_tags=suppressed_conceptual,
                entity_tags=entities_list,
                topic_tags=topics_list,
            )

        logger.debug(f"Using sliding window for tagging ({tokens} tokens)")
        chunks = self.windowing_service.get_windows(text)

        # Aggregate and Normalize
        conceptual_counter: Counter[str] = Counter()
        all_entities = set()
        topics_dict = {}

        for chunk in chunks:
            window_result = self._extract_chunk(
                chunk,
                require_conceptual_tags=is_substantive,
                reuse_hints=reuse_hints,
                source_filename=source_filename,
            )
            self._validate_conceptual_tags(
                window_result.conceptual_tags, is_substantive=is_substantive
            )

            # Normalize and update
            for t in window_result.conceptual_tags:
                conceptual_counter.update([normalize_tag_component(t)])

            for e in window_result.entity_tags:
                parts = e.split("/")
                norm_parts = [normalize_tag_component(p) for p in parts]
                all_entities.add("/".join(norm_parts))

            for tr in window_result.topic_tags:
                parts = tr.topic.split("/")
                norm_parts = [normalize_tag_component(p) for p in parts]
                norm_topic = "/".join(norm_parts)
                if norm_topic not in topics_dict:
                    tr.topic = norm_topic
                    topics_dict[norm_topic] = tr

        # Take top 100 conceptual tags by frequency to ensure robust context
        top_conceptual = [tag for tag, _ in conceptual_counter.most_common(100)]

        # Apply global filtering and suppression
        filtered_conceptual = filter_low_value_tags(top_conceptual)
        entities_list = sorted(list(all_entities))
        topics_list = sorted(topics_dict.values(), key=lambda x: x.topic)
        topic_names = [t.topic for t in topics_list]
        suppressed_conceptual = suppress_duplicates(
            filtered_conceptual,
            entities_list,
            topic_names,
            protected_terms=protected_conceptual,
        )
        self._validate_conceptual_tags(suppressed_conceptual, is_substantive=is_substantive)

        return AggregatedTaggingResult(
            conceptual_tags=suppressed_conceptual,
            entity_tags=entities_list,
            topic_tags=topics_list,
        )

    def _extract_chunk(
        self,
        chunk: str,
        require_conceptual_tags: bool = True,
        reuse_hints: Any | None = None,
        source_filename: str | None = None,
    ) -> WindowTaggingResult:
        """
        Extracts tags from a single chunk of text using a non-thinking model.
        """
        prompt = self._generate_tagging_prompt(
            chunk, reuse_hints=reuse_hints, source_filename=source_filename
        )
        schema = SubstantiveWindowTaggingResult if require_conceptual_tags else WindowTaggingResult
        try:
            return self.client.extract_structured(
                prompt, schema, model=self.model_name, think=False
            )
        except TaggingQualityError:
            raise
        except Exception as e:
            logger.error(f"Error extracting tags from chunk: {e}")
            if require_conceptual_tags:
                raise TaggingQualityError(
                    "Tagging-quality failure: substantive document tagging did not produce "
                    "a valid conceptual_tags field."
                ) from e
            return WindowTaggingResult()

    def _is_substantive(self, text: str) -> bool:
        normalized = " ".join(text.lower().split())
        if not normalized:
            return False

        boilerplate_patterns = [
            r"^(this document is )?incorporated into the initial document( and cancelled)?\.?$",
            r"^cancelled\.?$",
            r"^canceled\.?$",
            r"^annul[eé]\.?$",
            r"^ce document est incorpor[eé] dans le document initial( et annul[eé])?\.?$",
        ]
        return not any(re.match(pattern, normalized) for pattern in boilerplate_patterns)

    def _validate_conceptual_tags(
        self, conceptual_tags: list[str], *, is_substantive: bool
    ) -> None:
        if not is_substantive:
            return
        if len(conceptual_tags) < MIN_SUBSTANTIVE_CONCEPTUAL_TAGS:
            raise TaggingQualityError(
                "Tagging-quality failure: substantive document returned fewer than "
                f"{MIN_SUBSTANTIVE_CONCEPTUAL_TAGS} conceptual_tags from the initial tagging pass."
            )

    def _format_reuse_hints(self, reuse_hints: Any | None) -> str:
        if not reuse_hints:
            return ""

        lines = []
        conceptual = getattr(reuse_hints, "preferred_conceptual_tags", []) or []
        entities = getattr(reuse_hints, "preferred_entities", {}) or {}
        topics = getattr(reuse_hints, "preferred_topics", []) or []

        if conceptual:
            lines.append("RESUMED #Tags PREFERRED VOCABULARY:")
            lines.append(", ".join(conceptual))
        if entities:
            entity_lines = []
            for etype, values in entities.items():
                if values:
                    entity_lines.append(f"- {etype}: {', '.join(values)}")
            if entity_lines:
                lines.append("RESUMED #Entities PREFERRED VOCABULARY:")
                lines.extend(entity_lines)
        if topics:
            lines.append("RESUMED #Topics HINTS (subordinate to taxonomy):")
            lines.append(", ".join(topics))

        return "\n".join(lines)

    def _protected_conceptual_terms(self, reuse_hints: Any | None) -> set[str]:
        protected = {tag.lower() for tag in self.useful_tags}
        conceptual = getattr(reuse_hints, "preferred_conceptual_tags", []) or []
        protected.update(normalize_tag_component(tag).lower() for tag in conceptual)
        return protected

    def _generate_tagging_prompt(
        self,
        text: str,
        reuse_hints: Any | None = None,
        source_filename: str | None = None,
    ) -> str:
        """
        Generates the prompt for the tagging pass.
        """
        reuse_hint_text = self._format_reuse_hints(reuse_hints)
        reuse_section = f"\n\n{reuse_hint_text}\n" if reuse_hint_text else "\n"
        filename_section = ""
        if source_filename:
            filename_section = (
                "Source Relative Filename:\n"
                f"{source_filename}\n\n"
                "Use this filename as contextual evidence for archival code, document "
                "year/date, series, collection, or folder context when it is consistent "
                "with the full document text. Do not let filename context override clearly "
                "contradictory document text.\n\n"
            )
        return (
            f"{filename_section}"
            "Full Document Text:\n\n"
            f"{text}\n\n"
            "Based on the content above, extract precision tags in this order:\n\n"
            "1. 'topic_tags': Categories/Topics first. This is a mandatory multi-label "
            "taxonomy classification step, not optional context. Review the full APPROVED "
            "TAXONOMY and identify every clearly justified taxonomy topic supported by the "
            "full document text, not just the single best or most obvious topic. Use format: "
            "Category/Topic. A document may match multiple topics across different categories. "
            "Include every supported topic with a brief 'reason' containing direct quoted "
            "evidence. Do not stop after finding one matching topic. Use an empty list only "
            "when no approved taxonomy topic is supported by the full document text.\n"
            "   MANDATORY: When providing a 'reason', include direct citations in double "
            "quotes from the text to justify the topic selection.\n"
            "2. 'entity_tags': Entities second. Hierarchical tags for mentioned entities. "
            "Use formats: State/<name>, Org/<name>, City/<country>/<city>, Person/<name>.\n"
            "   STRICT ENTITY NORMALIZATION:\n"
            "   - Use English canonical names for States, Organisations, and Cities whenever "
            "the intended entity is clear. For example, use 'Germany' not 'Allemagne', "
            "'United-Kingdom' not 'Royaume-Uni', 'United-States' not 'USA', "
            "'Brussels' not 'Bruxelles', and 'The-Hague' not 'La-Haye'.\n"
            "   - Use Title Case for State, City, Person, and Organisation names; preserve "
            "ALL CAPS only for standard acronyms such as NATO, SHAPE, NPG, SACLANT, "
            "SACEUR, and DPC. Never output entity names in lowercase.\n"
            "   - Prefer standard acronyms for well-known organisations when they are the "
            "canonical form: use 'NATO' for OTAN or Organisation du Traite de "
            "l'Atlantique Nord, and use 'SHAPE', 'NPG', 'SACLANT', 'SACEUR', and "
            "'DPC' where appropriate.\n"
            "   - Correct obvious OCR damage in known entity names only when surrounding "
            "context makes the intended entity unambiguous. For example, treat "
            "'Nuclear Planning Group ST/FF Group', 'Nuclear Planning Group Sta-F Group', "
            "and 'Nuclear Planning Group St-1F Group' as the standard Nuclear Planning "
            "Group Staff Group entity.\n"
            "   - Do not invent a canonical entity from ambiguous OCR-damaged text. If the "
            "intended State, Organisation, City, or Person is unclear, omit that entity.\n"
            "   - Keep City tags as City/<country>/<city>; do not emit regions, states, or "
            "countries as cities.\n"
            "3. 'conceptual_tags': Tags last. Required canonical tag paths for archivally substantive "
            f"concepts. Return at least {MIN_SUBSTANTIVE_CONCEPTUAL_TAGS} conceptual tag(s) "
            "for substantive documents; include "
            "every clearly justified useful conceptual tag; return an empty list only for "
            "non-substantive administrative stubs. "
            "PRIORITIZE re-using tags from the vocabularies below. Normalize exercises as Name/YY. "
            "MANDATORY: Include all all-caps abbreviations mentioned in the text "
            "when they are meaningful acronyms.\n\n"
            "EXAMPLES OF CORRECT ENTITY EXTRACTION:\n"
            "- Text: 'Un compte rendu de la reunion a Bruxelles...'\n"
            "  -> entity_tags: ['City/Belgium/Brussels']\n"
            "- Text: 'agreed by l\\'OTAN and SACEUR'\n"
            "  -> entity_tags: ['Org/NATO', 'Org/SACEUR']\n"
            "- Text: 'represented by Allemagne, Royaume-Uni, and USA'\n"
            "  -> entity_tags: ['State/Germany', 'State/United-Kingdom', "
            "'State/United-States']\n"
            "- Text: 'The Nuclear Planning Group ST/FF Group met...'\n"
            "  -> entity_tags: ['Org/Nuclear-Planning-Group-Staff-Group']\n"
            "- Text: 'discussions on the PERSHING missile system...'\n"
            "  -> conceptual_tags: ['Pershing']\n\n"
            "APPROVED TAXONOMY (YAML):\n"
            f"{self.taxonomy_prompt_text}\n\n"
            "EXISTING VOCABULARY (USEFUL TAGS):\n"
            f"{self.useful_tags_prompt_text}"
            f"{reuse_section}\n"
            "CRITICAL RULES:\n"
            "- Only include tags that are clearly justified by the text.\n"
            "- Output order matters for LLM decoding: fill topic_tags first, entity_tags "
            "second, and conceptual_tags last.\n"
            "- Exclude routine administrative labels (agenda, report, notice, corrigendum).\n"
            "- Ensure hierarchical formats are strictly followed.\n"
            "- For entities, use English canonical names, Title Case, standard acronyms, "
            "and conservative OCR recovery as instructed above.\n"
            "- STRICT ENTITY/TAG SEPARATION: After choosing entity_tags, treat every entity "
            "name and normalized variant as forbidden for conceptual_tags. Do not create a "
            "#Tags entry for any organisation, state, city, or person already represented "
            "in entity_tags, including exact names, aliases, translated forms, acronyms, "
            "expanded names, punctuation/case variants, hyphenation variants, or compacted "
            "forms such as 'NuclearPlanningGroup'. For example, if entity_tags contains "
            "'Org/NATO', do not emit conceptual tags 'NATO', 'OTAN', or "
            "'NorthAtlanticTreatyOrganization'; if entity_tags contains 'Org/NPG', do not "
            "emit 'NPG' or 'NuclearPlanningGroup' as conceptual tags. Only emit a related "
            "conceptual tag when it names a distinct archival concept, policy, system, "
            "exercise, procedure, or event beyond the entity itself.\n"
            "- Do not emit both an abbreviation and its expanded full-name form as conceptual "
            "tags when they refer to the same concept. Choose one canonical form, preferring "
            "the standard acronym for well-known NATO-domain terms (e.g., use 'NPG' instead "
            "of 'NuclearPlanningGroup', and 'NATO' instead of 'NorthAtlanticTreatyOrganization').\n"
            "- If an entity or concept is in ALL-CAPS but is NOT an abbreviation "
            "(e.g., PERSHING), generate the tag in Title Case (e.g., Pershing)."
        )
