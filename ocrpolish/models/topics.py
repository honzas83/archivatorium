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


class FlatTopicAssignment(BaseModel):
    """A single topic assignment in a flat hierarchy pass."""
    topic_id: str = Field(..., description="The ID of the topic (e.g., 'Category/Topic').")
    reason: str = Field(..., description="The reason why this topic should be assigned.")


class FlatTopicSelectionSchema(BaseModel):
    """Schema for single-step flat topic selection."""
    assignments: list[FlatTopicAssignment] = Field(
        ...,
        description="List of specific topic assignments (at most 3).",
        max_length=3
    )
