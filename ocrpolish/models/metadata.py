from pydantic import BaseModel, Field


class CorrespondenceSchema(BaseModel):
    sender: str = Field("", description="The name and/or institution of the sender.")
    recipient: str = Field("", description="The name and/or institution of the recipient.")
    transaction: str = Field(
        "", 
        description="The specific action, request, or purpose imposed by the correspondence."
    )

class MetadataSchema(BaseModel):
    title: str = Field(
        "", 
        description=(
            "The formal title of the document. Extract it carefully, looking at the first "
            "two pages if necessary (e.g., in correspondence). The title must be "
            "contextually consistent with the summary and abstract."
        )
    )
    summary: str = Field(
        "",
        description=(
            "A concise summary of the document, limited to exactly two sentences. "
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
        )
    )
    author_name: str = Field("", description="The name of the officer or individual author.")
    author_institution: str = Field(
        "", description="The organization or institution responsible for the document."
    )
    date: str = Field(
        "", 
        description="The complete date of the document in ISO 8601 format (YYYY-MM-DD)."
    )
    archive_code: str = Field(
        "", 
        description="The formal archive reference code (e.g., NPG/D(77)12)."
    )
    language: str = Field("English", description="Primary language of the document.")
    location_city: str = Field("", description="The city where the document originated.")
    location_state: str = Field("", description="The nation-state where the document originated.")
    
    # Flattened correspondence fields to avoid nested object grammar issues
    correspondence_sender: str = Field("", description="The name/institution of the sender.")
    correspondence_recipient: str = Field("", description="The name/institution of the recipient.")
    correspondence_transaction: str = Field(
        "", description="The action, request, or purpose imposed by the correspondence."
    )
    
    mentioned_states: list[str] = Field(
        default_factory=list, 
        description="Full names of national states mentioned (e.g., United Kingdom)."
    )
    mentioned_organisations: list[str] = Field(
        default_factory=list, 
        description="Organizations mentioned (e.g., NATO, European Community)."
    )
    references: list[str] = Field(
        default_factory=list,
        description="Other archive reference codes mentioned (e.g., C-M(55)15)."
    )
    tags: list[str] = Field(
        default_factory=list,
        description=(
            "Arbitrary, hash-tag like keywords (3-8). MUST NOT contain spaces "
            "(e.g., #NuclearPlanning)."
        ),
    )

class LastDateSchema(BaseModel):
    date: str = Field(
        "", 
        description="The document date in ISO 8601 format (YYYY-MM-DD)."
    )
