"""Routes for action item extraction and management."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemDetail,
    ActionItemResponse,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    try:
        items = extract_action_items_llm(payload.text)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.get("", response_model=List[ActionItemDetail])
def list_all(note_id: Optional[int] = None) -> List[ActionItemDetail]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemDetail(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    db.mark_action_item_done(action_item_id, payload.done)
    return MarkDoneResponse(id=action_item_id, done=payload.done)
