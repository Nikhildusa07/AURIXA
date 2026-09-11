from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequestCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=255,
    )

    content: str = Field(
        min_length=1,
    )

    request_type: str | None = Field(
        default="general",
        max_length=50,
    )

    priority: str | None = Field(
        default="normal",
        max_length=50,
    )


class RequestResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_id: UUID | None
    title: str
    content: str
    request_type: str | None
    status: str
    priority: str | None
    confidence_score: float | None
    result: dict | None
    trace_id: str