from pydantic import BaseModel, Field


class CategorySelectionSchema(BaseModel):
    """Schema for the first step: selecting applicable categories."""
    selected_categories: list[str] = Field(
        ..., description="List of category names that apply to the document."
    )


class TopicAssignment(BaseModel):
    """A single topic assignment within a category."""
    category: str = Field(..., description="The name of the category.")
    topic: str = Field(..., description="The name of the topic.")
    reason: str = Field(..., description="The reason why this topic should be assigned.")


class TopicSelectionSchema(BaseModel):
    """Schema for the second step: selecting specific topics within categories."""
    assignments: list[TopicAssignment] = Field(
        ..., 
        description="List of specific topic assignments (at most 3).",
        max_length=3
    )
