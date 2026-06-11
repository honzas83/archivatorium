from pydantic import BaseModel, Field


MIN_SUBSTANTIVE_CONCEPTUAL_TAGS = 3


class CorrespondenceSchema(BaseModel):
    sender: str = Field("", description="The name and/or institution of the sender.")
    recipient: str = Field("", description="The name and/or institution of the recipient.")
    correspondence: str = Field(
        "", description="The specific action, request, or purpose imposed by the correspondence."
    )


class MetadataSchema(BaseModel):
    title: str = Field(
        "",
        description=(
            "The formal title of the document. MANDATORY: Extract it in its ORIGINAL LANGUAGE. "
            "DO NOT use ALL UPPERCASE. Use natural casing appropriate for the language: "
            "for English, you MUST use Title Case (e.g., 'Meeting of the Planning Group'); "
            "for French, you MUST use Sentence case (e.g., 'Réunion du groupe'). "
            "Extract carefully from first two pages."
        ),
    )
    summary: str = Field(
        "",
        description=(
            "A concise summary of the document, limited to exactly one sentence. "
            "This must be an independent entity; define any abbreviations naturally "
            "within the text."
        ),
    )
    abstract: str = Field(
        "",
        description=(
            "A detailed overview of the document content, limited to at most 20 sentences. "
            "This must be a superset of the summary (incorporating its information) and "
            "remain an independent entity; redefine any abbreviations naturally within the text."
        ),
    )
    author_name: str = Field("", description="The name of the officer or individual author.")
    author_institution: str = Field(
        "", description="The organization or institution responsible for the document."
    )
    date: str = Field(
        "", description="The complete date of the document in ISO 8601 format (YYYY-MM-DD)."
    )
    archive_code: str = Field(
        "", description="The formal archive reference code (e.g., NPG/D(77)12)."
    )
    language: str = Field("English", description="Primary language of the document.")
    location_city: str = Field("", description="The city where the document originated.")
    location_state: str = Field("", description="The nation-state where the document originated.")

    # Flattened correspondence fields
    sender: str = Field("", description="The name/institution of the sender.")
    recipient: str = Field("", description="The name/institution of the recipient.")
    intent: str = Field(
        "", description="The action, request, or purpose imposed by the correspondence."
    )

    references: list[str] = Field(
        default_factory=list,
        description="Other archive reference codes mentioned (e.g., C-M(55)15).",
    )


class LastDateSchema(BaseModel):
    date: str = Field("", description="The document date in ISO 8601 format (YYYY-MM-DD).")


class TopicResult(BaseModel):
    """A topic assignment with its reasoning."""

    topic: str = Field(..., description="The hierarchical topic tag (e.g., 'Category/Topic').")
    reason: str = Field(..., description="Brief reason for assigning this topic.")


class WindowTaggingResult(BaseModel):
    """Raw output from the LLM for a single chunk or entire document pass."""

    conceptual_tags: list[str] = Field(
        default_factory=list,
        description=(
            "Canonical conceptual tag paths from USEFUL_TAGS.yaml, resumed #Tags counters, "
            "or new canonical forms justified by the source text."
        ),
    )
    entity_tags: list[str] = Field(
        default_factory=list,
        description="Hierarchical tags: State/X, Org/X, City/State/City, Person/X.",
    )
    topic_tags: list[TopicResult] = Field(
        default_factory=list,
        description=(
            "List of every clearly justified hierarchical taxonomy topic with its reason."
        ),
    )


class SubstantiveWindowTaggingResult(WindowTaggingResult):
    """Raw tagging output required for substantive document text."""

    conceptual_tags: list[str] = Field(
        ...,
        min_length=MIN_SUBSTANTIVE_CONCEPTUAL_TAGS,
        description=(
            "Required for substantive documents. Return at least "
            f"{MIN_SUBSTANTIVE_CONCEPTUAL_TAGS} conceptual tags; include every clearly "
            "justified useful conceptual tag. Do not impose a hard maximum."
        ),
    )


class AggregatedTaggingResult(BaseModel):
    """Final deduplicated and suppressed result for the entire document."""

    conceptual_tags: list[str] = Field(
        default_factory=list,
        description=(
            "Frequency-weighted, normalized, duplicate-suppressed conceptual tags. "
            "Substantive documents must retain at least "
            f"{MIN_SUBSTANTIVE_CONCEPTUAL_TAGS} useful tags."
        ),
    )
    entity_tags: list[str] = Field(default_factory=list, description="Set union of all entities.")
    topic_tags: list[TopicResult] = Field(
        default_factory=list,
        description="Set union of all clearly justified topics with best available reasons.",
    )


class CanonicalTags(BaseModel):
    """Structured, normalized canonical tags parsed from Markdown."""

    conceptual_tags: set[str] = Field(default_factory=set)
    topics: set[str] = Field(default_factory=set)
    entities: dict[str, set[str]] = Field(
        default_factory=lambda: {
            "State": set[str](),
            "Org": set[str](),
            "City": set[str](),
            "Person": set[str](),
        }
    )
    raw_paths: set[str] = Field(default_factory=set)
