import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from archivatorium.models.metadata import (
    MAX_CONCEPTUAL_TAGS,
    MAX_NOVEL_CONCEPTUAL_TAGS,
    MIN_SUBSTANTIVE_CONCEPTUAL_TAGS,
    TARGET_MAX_CONCEPTUAL_TAGS,
    TARGET_MIN_CONCEPTUAL_TAGS,
    AggregatedTaggingResult,
    SubstantiveWindowTaggingResult,
    TopicResult,
    WindowTaggingResult,
)
from archivatorium.services.flattening_service import (
    FlatteningService,
    TaxonomyValidationError,
)
from archivatorium.services.ollama_client import OllamaClient
from archivatorium.services.windowing_service import SlidingWindowService
from archivatorium.utils.model_think import MODEL_THINK_DEFAULT, ModelThink
from archivatorium.utils.nlp import (
    conceptual_tag_key,
    estimate_tokens,
    filter_low_value_tags,
    normalize_tag_component,
    suppress_duplicates,
)
from archivatorium.utils.person_entities import normalize_person_path

logger = logging.getLogger(__name__)

DEFAULT_CLASSIFICATION_POLICY = {
    "substantive_subject_rule": (
        "Assign a topic only when it is an important subject of the document, demonstrated "
        "through analysis, decision, proposal, recommendation, operational treatment, or "
        "sustained description."
    ),
    "omission_rule": (
        "Prefer omission over a weak or incidental match; an empty thematic-topic list is valid."
    ),
    "insufficient_evidence_rule": (
        "A keyword, named entity, country, organization, meeting, citation, document title, "
        "distribution-list entry, or single passing reference is insufficient by itself."
    ),
}


class TaggingQualityError(RuntimeError):
    """Raised when a substantive document receives an unacceptable tagging result."""


@dataclass
class _ConceptualAggregate:
    display_value: str
    window_count: int
    best_rank: int
    first_seen: int


class TaggingService:
    """
    Service for extracting tiered tags (Entities, Topics, Conceptual)
    using a dynamic single-pass or sliding-window strategy.
    """

    def __init__(
        self,
        ollama_client: OllamaClient,
        windowing_service: SlidingWindowService,
        themes_path: Path,
        useful_tags_path: Path | None = None,
        context_limit: int = 32000,
        model_name: str = "gemma4:31b",
        model_think: ModelThink = MODEL_THINK_DEFAULT,
    ):
        self.client = ollama_client
        self.windowing_service = windowing_service
        self.themes_path = themes_path
        self.useful_tags_path = useful_tags_path
        self.context_limit = context_limit
        self.model_name = model_name
        self.model_think = model_think
        self.flattening_service = FlatteningService()

        # Load and Normalize Themes
        raw_themes = self._load_yaml(themes_path, label="taxonomy")
        self.themes = self._normalize_data(raw_themes)
        self.flattened_taxonomy = self.flattening_service.flatten(self.themes)
        self.approved_topic_ids = {str(topic["id"]) for topic in self.flattened_taxonomy}
        self.classification_policy = self._effective_classification_policy(self.themes)
        self.classification_policy_prompt_text = "\n".join(
            f"- {value}" for value in self.classification_policy.values()
        )
        self.taxonomy_prompt_text = yaml.dump(
            {
                "classification_policy": self.classification_policy,
                "topics": self.flattened_taxonomy,
            },
            sort_keys=False,
        )

        # Load and Normalize Useful Tags
        self.useful_tags = []
        if useful_tags_path:
            raw_tags = self._load_yaml(useful_tags_path, label="useful tags").get("useful_tags", [])
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

    @staticmethod
    def _effective_classification_policy(themes: dict[str, Any]) -> dict[str, str]:
        policy = themes.get("classification_policy")
        if not isinstance(policy, dict):
            return dict(DEFAULT_CLASSIFICATION_POLICY)
        return {
            key: str(policy.get(key, default))
            for key, default in DEFAULT_CLASSIFICATION_POLICY.items()
        }

    def _load_yaml(self, path: Path, *, label: str) -> dict[str, Any]:
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as exc:
            raise TaxonomyValidationError(
                f"Failed to load {label} YAML from {path}: {exc}"
            ) from exc
        if not isinstance(data, dict):
            raise TaxonomyValidationError(
                f"Failed to load {label} YAML from {path}: root must be a mapping."
            )
        return data

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
        known_conceptual = self._known_conceptual_terms(reuse_hints)

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
            entities_list = sorted(self._normalize_entities(window_result.entity_tags))

            # Normalize approved topics and keep the earliest reason.
            topics_dict = self._collect_supported_topics(window_result.topic_tags)

            topics_list = sorted(topics_dict.values(), key=lambda x: x.topic)
            topic_names = [t.topic for t in topics_list]

            conceptual_tags = self._finalize_conceptual_tags(
                window_result.conceptual_tags,
                entities_list,
                topic_names,
                known_conceptual,
            )

            return AggregatedTaggingResult(
                conceptual_tags=conceptual_tags,
                entity_tags=entities_list,
                topic_tags=topics_list,
            )

        logger.debug(f"Using sliding window for tagging ({tokens} tokens)")
        chunks = self.windowing_service.get_windows(text)

        # Aggregate and Normalize
        conceptual_aggregates: dict[str, _ConceptualAggregate] = {}
        first_seen = 0
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

            first_seen = self._update_conceptual_aggregates(
                conceptual_aggregates,
                window_result.conceptual_tags,
                first_seen,
            )

            all_entities.update(self._normalize_entities(window_result.entity_tags))

            self._collect_supported_topics(window_result.topic_tags, topics_dict)

        ranked_conceptual = [
            aggregate.display_value
            for aggregate in sorted(
                conceptual_aggregates.values(),
                key=lambda item: (-item.window_count, item.best_rank, item.first_seen),
            )
        ]

        entities_list = sorted(all_entities)
        topics_list = sorted(topics_dict.values(), key=lambda x: x.topic)
        topic_names = [t.topic for t in topics_list]
        conceptual_tags = self._finalize_conceptual_tags(
            ranked_conceptual,
            entities_list,
            topic_names,
            known_conceptual,
        )

        return AggregatedTaggingResult(
            conceptual_tags=conceptual_tags,
            entity_tags=entities_list,
            topic_tags=topics_list,
        )

    @staticmethod
    def _update_conceptual_aggregates(
        aggregates: dict[str, _ConceptualAggregate],
        tags: list[str],
        first_seen: int,
    ) -> int:
        seen_in_window: set[str] = set()
        for rank, tag in enumerate(tags):
            display_value = normalize_tag_component(tag)
            key = conceptual_tag_key(display_value)
            if not key:
                continue
            aggregate = aggregates.get(key)
            if aggregate is None:
                aggregate = _ConceptualAggregate(display_value, 0, rank, first_seen)
                aggregates[key] = aggregate
                first_seen += 1
            else:
                aggregate.best_rank = min(aggregate.best_rank, rank)
            if key not in seen_in_window:
                aggregate.window_count += 1
                seen_in_window.add(key)
        return first_seen

    @staticmethod
    def _normalize_entities(entity_tags: list[str]) -> set[str]:
        normalized_entities: set[str] = set()
        for entity in entity_tags:
            if entity.split("/", 1)[0].lower() == "person":
                normalized_person = normalize_person_path(entity)
                if normalized_person is None:
                    logger.warning("Dropping malformed Person entity: %s", entity)
                    continue
                normalized_entities.add(normalized_person)
                continue

            parts = entity.split("/")
            norm_parts = [normalize_tag_component(part) for part in parts]
            normalized_entities.add("/".join(norm_parts))
        return normalized_entities

    def _collect_supported_topics(
        self,
        topic_tags: list[TopicResult],
        collected: dict[str, TopicResult] | None = None,
    ) -> dict[str, TopicResult]:
        results = collected if collected is not None else {}
        for topic_result in topic_tags:
            normalized_topic = "/".join(
                normalize_tag_component(part) for part in topic_result.topic.split("/")
            )
            if normalized_topic not in self.approved_topic_ids:
                logger.warning("Dropping unsupported taxonomy topic: %s", normalized_topic)
                continue
            if normalized_topic not in results:
                topic_result.topic = normalized_topic
                results[normalized_topic] = topic_result
        return results

    def _extract_chunk(
        self,
        chunk: str,
        require_conceptual_tags: bool = True,
        reuse_hints: Any | None = None,
        source_filename: str | None = None,
    ) -> WindowTaggingResult:
        """
        Extracts tags from a single chunk using the command-scoped reasoning setting.
        """
        prompt = self._generate_tagging_prompt(
            chunk, reuse_hints=reuse_hints, source_filename=source_filename
        )
        schema = SubstantiveWindowTaggingResult if require_conceptual_tags else WindowTaggingResult
        try:
            return self.client.extract_structured(
                prompt, schema, model=self.model_name, think=self.model_think
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

    def _known_conceptual_terms(self, reuse_hints: Any | None) -> set[str]:
        known = {conceptual_tag_key(tag) for tag in self.useful_tags}
        conceptual = getattr(reuse_hints, "preferred_conceptual_tags", []) or []
        known.update(conceptual_tag_key(tag) for tag in conceptual)
        return known

    @staticmethod
    def _finalize_conceptual_tags(
        candidates: list[str],
        entities: list[str],
        topics: list[str],
        known_conceptual: set[str],
    ) -> list[str]:
        normalized = [normalize_tag_component(tag) for tag in candidates]
        filtered = filter_low_value_tags([tag for tag in normalized if tag])
        separated = suppress_duplicates(
            filtered,
            entities,
            topics,
            protected_terms=known_conceptual,
        )

        unique = TaggingService._deduplicate_conceptual_tags(separated)
        retained: list[str] = []
        novel_count = 0
        for tag in unique:
            key = conceptual_tag_key(tag)
            is_novel = key not in known_conceptual
            if is_novel and novel_count >= MAX_NOVEL_CONCEPTUAL_TAGS:
                continue
            if len(retained) >= MAX_CONCEPTUAL_TAGS:
                break
            retained.append(tag)
            if is_novel:
                novel_count += 1
        return retained

    @staticmethod
    def _deduplicate_conceptual_tags(candidates: list[str]) -> list[str]:
        unique: list[str] = []
        seen: set[str] = set()
        for tag in candidates:
            key = conceptual_tag_key(tag)
            if key and key not in seen:
                seen.add(key)
                unique.append(tag)
        return unique

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
            "UNIVERSAL THEMATIC TOPIC POLICY:\n"
            f"{self.classification_policy_prompt_text}\n\n"
            "Based on the content above, extract precision tags in this order:\n\n"
            "1. 'topic_tags': Categories/Topics first. This is a mandatory multi-label "
            "taxonomy classification step, not optional context. Review the full APPROVED "
            "TAXONOMY and identify every substantively supported taxonomy topic for which the "
            "defining relationship is an important document subject. Use format: "
            "Category/Topic. A document may match multiple topics across different categories. "
            "Include every substantively supported topic with a brief 'reason' containing direct "
            "quoted evidence, but omit marginal or incidental matches. Use an empty list when no "
            "approved taxonomy topic is a substantive subject of the full document text.\n"
            "   MANDATORY: When providing a 'reason', include direct citations in double "
            "quotes from the text to justify the topic selection.\n"
            "2. 'entity_tags': Entities second. Hierarchical tags for mentioned entities. "
            "Use formats: State/<name>, Org/<name>, City/<country>/<city>, "
            "Person/<surname>[/<given-name-or-initials>].\n"
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
            "   - For people, put the surname first and the given name or initials second. "
            "Join separate initials with hyphens: K-W Andrae becomes Person/Andrae/K-W; "
            "Joseph M.A.H. Luns becomes Person/Luns/Joseph-M-A-H. If only the surname is "
            "known, use the surname-only form, for example Person/Andrae.\n"
            "   - Never add a role, title, rank, or office such as minister or secretary to "
            "a Person path. Omit those modifiers rather than treating them as names.\n"
            "3. 'conceptual_tags': Tags last. Return canonical paths for the principal archivally "
            f"substantive concepts in descending order of importance. For a substantive document, "
            f"normally return {TARGET_MIN_CONCEPTUAL_TAGS} to {TARGET_MAX_CONCEPTUAL_TAGS}; return "
            "fewer when fewer concepts are supported, and return an empty list only for a "
            "non-substantive administrative stub. Do not add weak tags to fill the target range. "
            "Treat USEFUL TAGS and resumed established tags as preferred seed vocabulary, not an "
            "allowlist. Prefer an available canonical seed or established tag for the same concept, "
            "but allow a genuinely distinct novel concept supported by the document. Normalize "
            "exercises as Name/YY.\n\n"
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
            "- Text: 'K. W. Andrae and Joseph M.A.H. Luns attended'\n"
            "  -> entity_tags: ['Person/Andrae/K-W', 'Person/Luns/Joseph-M-A-H']\n"
            "- Text: 'discussions on the PERSHING missile system...'\n"
            "  -> conceptual_tags: ['Pershing']\n\n"
            "APPROVED TAXONOMY (YAML):\n"
            f"{self.taxonomy_prompt_text}\n\n"
            "EXISTING VOCABULARY (USEFUL TAGS):\n"
            f"{self.useful_tags_prompt_text}"
            f"{reuse_section}\n"
            "CRITICAL RULES:\n"
            "- Only include thematic topics that are important, substantively treated subjects.\n"
            "- Do not include a topic for a keyword or passing reference alone. Prefer omission.\n"
            "- Output order matters for LLM decoding: fill topic_tags first, entity_tags "
            "second, and conceptual_tags last.\n"
            "- Order conceptual_tags from most important to least important.\n"
            "- A conceptual tag must be directly and substantively discussed through analysis, "
            "decision, proposal, recommendation, operational treatment, or sustained description. "
            "Do not tag an implication, passing mention, or mere lexical association.\n"
            "- Do not manufacture Cartesian-product tag families. Do not add synonyms, grammatical "
            "variants, or broader/narrower variants unless each is a distinct concept independently "
            "and substantively discussed.\n"
            "- The same rules apply to acronyms: keep a meaningful acronym only when it names a "
            "substantive concept, and classify an organization acronym only as an entity.\n"
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
