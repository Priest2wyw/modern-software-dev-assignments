from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import ErrorResponse, NoteCreateRequest, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=500, detail="created note could not be loaded")
    return NoteResponse(**note)


@router.get("/{note_id}", response_model=NoteResponse, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def get_single_note(note_id: int) -> NoteResponse:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(**row)

