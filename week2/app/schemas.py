"""Pydantic models defining API request/response contracts."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ---- Notes ----

class NoteCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Note text content")


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


# ---- Action Items ----

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Free-form text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to persist the text as a note")


class ActionItemResponse(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: List[ActionItemResponse]


class ActionItemDetail(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str


class MarkDoneRequest(BaseModel):
    done: bool = Field(default=True)


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
