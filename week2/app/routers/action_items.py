from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..db import RecordNotFoundError
from ..schemas import (
    ActionItemResponse,
    ErrorResponse,
    ExtractActionItemsRequest,
    ExtractActionItemsResponse,
    ExtractedActionItemResponse,
    MarkActionItemDoneRequest,
    MarkActionItemDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post(
    "/extract",
    response_model=ExtractActionItemsResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def extract(payload: ExtractActionItemsRequest) -> ExtractActionItemsResponse:
    items = extract_action_items(payload.text)
    note_id = db.insert_note(payload.text) if payload.save_note else None
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractActionItemsResponse(
        note_id=note_id,
        items=[ExtractedActionItemResponse(id=item_id, text=text) for item_id, text in zip(ids, items)],
    )


@router.post(
    "/extract-llm",
    response_model=ExtractActionItemsResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def extract_llm(payload: ExtractActionItemsRequest) -> ExtractActionItemsResponse:
    items = extract_action_items_llm(payload.text)
    note_id = db.insert_note(payload.text) if payload.save_note else None
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractActionItemsResponse(
        note_id=note_id,
        items=[ExtractedActionItemResponse(id=item_id, text=text) for item_id, text in zip(ids, items)],
    )


@router.get("", response_model=list[ActionItemResponse], responses={500: {"model": ErrorResponse}})
def list_all(note_id: int | None = None) -> list[ActionItemResponse]:
    rows = db.list_action_items(note_id=note_id)
    return [ActionItemResponse(**row) for row in rows]


@router.post(
    "/{action_item_id}/done",
    response_model=MarkActionItemDoneResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def mark_done(action_item_id: int, payload: MarkActionItemDoneRequest) -> MarkActionItemDoneResponse:
    try:
        db.mark_action_item_done(action_item_id, payload.done)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MarkActionItemDoneResponse(id=action_item_id, done=payload.done)
