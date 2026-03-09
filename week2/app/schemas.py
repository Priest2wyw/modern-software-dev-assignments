from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ErrorResponse(APIModel):
    detail: str


class NoteCreateRequest(APIModel):
    content: str = Field(..., description="Raw note content")

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value:
            raise ValueError("content is required")
        return value


class NoteResponse(APIModel):
    id: int
    content: str
    created_at: str


class ExtractActionItemsRequest(APIModel):
    text: str = Field(..., description="Source text to analyze")
    save_note: bool = False

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value:
            raise ValueError("text is required")
        return value


class ExtractedActionItemResponse(APIModel):
    id: int
    text: str


class ExtractActionItemsResponse(APIModel):
    note_id: int | None = None
    items: list[ExtractedActionItemResponse]


class ActionItemResponse(APIModel):
    id: int
    note_id: int | None = None
    text: str
    done: bool
    created_at: str


class MarkActionItemDoneRequest(APIModel):
    done: bool = True


class MarkActionItemDoneResponse(APIModel):
    id: int
    done: bool
