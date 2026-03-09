from __future__ import annotations

import pytest
from types import SimpleNamespace

from fastapi import HTTPException
from pydantic import ValidationError

from ..app import config
from ..app.db import init_db
from ..app.main import create_app
from ..app.routers.action_items import extract, list_all, mark_done
from ..app.routers.notes import create_note, get_single_note
from ..app.services import extract as extract_service
from ..app.schemas import (
    ExtractActionItemsRequest,
    MarkActionItemDoneRequest,
    NoteCreateRequest,
)


def configure_test_settings(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("APP_TITLE", "Action Item Extractor Test")
    monkeypatch.setenv("WEEK2_DB_PATH", str(tmp_path / "test.db"))
    config.get_settings.cache_clear()
    init_db()


def test_app_uses_cached_settings(tmp_path, monkeypatch):
    configure_test_settings(tmp_path, monkeypatch)

    app = create_app()

    assert app.title == "Action Item Extractor Test"
    assert app.state.settings.db_path == tmp_path / "test.db"


def test_note_schema_rejects_blank_content():
    with pytest.raises(ValidationError, match="content is required"):
        NoteCreateRequest(content="   ")


def test_create_and_fetch_note(tmp_path, monkeypatch):
    configure_test_settings(tmp_path, monkeypatch)

    created = create_note(NoteCreateRequest(content=" Ship week 2 assignment "))
    fetched = get_single_note(created.id)

    assert created.content == "Ship week 2 assignment"
    assert fetched.id == created.id
    assert fetched.content == "Ship week 2 assignment"


def test_extract_and_list_action_items(tmp_path, monkeypatch):
    configure_test_settings(tmp_path, monkeypatch)

    class FakeClient:
        def __init__(self, host):
            self.host = host

        def chat(self, *, model, messages, format):
            return SimpleNamespace(
                message=SimpleNamespace(content='["Set up database", "Write tests"]')
            )

    monkeypatch.setattr(extract_service, "Client", FakeClient)

    response = extract(
        ExtractActionItemsRequest(text="- [ ] Set up database\n1. Write tests", save_note=True)
    )
    items = list_all(note_id=response.note_id)

    assert response.note_id is not None
    assert [item.text for item in response.items] == ["Set up database", "Write tests"]
    assert [item.text for item in items] == ["Write tests", "Set up database"]


def test_mark_done_returns_404_for_missing_item(tmp_path, monkeypatch):
    configure_test_settings(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        mark_done(999, MarkActionItemDoneRequest(done=True))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Action item 999 not found"
