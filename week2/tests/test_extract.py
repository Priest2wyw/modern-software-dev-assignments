from types import SimpleNamespace

from ..app.services import extract
import pytest

from ..app.services.extract import ExtractionError, extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            self.host = host

        def chat(self, *, model, messages, format):
            return SimpleNamespace(
                message=SimpleNamespace(
                    content='["Set up database", "implement API extract endpoint", "Write tests"]'
                )
            )

    monkeypatch.setattr(extract, "Client", FakeClient)

    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_handles_mixed_todo_text():
    text = """
    there are todo list
    - write a front-web
    - [] write a backend serve
    write test
    fix the bug and re-test the code
    """.strip()

    items = extract_action_items(text)

    assert items == [
        "write a front-web",
        "write a backend serve",
        "write test",
        "fix the bug and re-test the code",
    ]


def test_extract_action_items_llm_returns_structured_items(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            assert host == "http://127.0.0.1:11435"

        def chat(self, *, model, messages, format):
            assert model == "test-model"
            assert messages[1]["content"].endswith("Note:\n- [ ] Set up database\n- Write tests")
            assert format == extract.ActionItemsResponse.model_json_schema()
            return SimpleNamespace(
                message=SimpleNamespace(
                    content='["Set up database", "Write tests", "Set up database"]'
                )
            )

    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11435")
    monkeypatch.setattr(extract, "Client", FakeClient)
    extract.get_settings.cache_clear()

    items = extract_action_items_llm("- [ ] Set up database\n- Write tests", model="test-model")
    extract.get_settings.cache_clear()

    assert items == ["Set up database", "Write tests"]


def test_extract_action_items_llm_cleans_prefixes(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            self.host = host

        def chat(self, *, model, messages, format):
            return SimpleNamespace(
                message=SimpleNamespace(content='["- [ ] Update README", "1. Write tests"]')
            )

    monkeypatch.setattr(extract, "Client", FakeClient)

    items = extract_action_items_llm("todo: update follow-up tasks")

    assert items == ["Update README", "Write tests"]


def test_extract_action_items_llm_skips_empty_input(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            raise AssertionError("Client should not be constructed for empty input")

    monkeypatch.setattr(extract, "Client", FakeClient)

    assert extract_action_items_llm("   ") == []


def test_extract_action_items_llm_reports_connection_details(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            assert host == "http://127.0.0.1:11435"

        def chat(self, *, model, messages, format):
            raise RuntimeError("connection refused")

    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11435")
    monkeypatch.setattr(extract, "Client", FakeClient)
    extract.get_settings.cache_clear()

    with pytest.raises(ExtractionError, match="Could not reach Ollama at http://127.0.0.1:11435"):
        extract_action_items_llm("Write tests", model="test-model")

    extract.get_settings.cache_clear()


def test_extract_action_items_llm_reports_invalid_structured_output(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            self.host = host

        def chat(self, *, model, messages, format):
            return SimpleNamespace(message=SimpleNamespace(content='{"items":["Write tests"]}'))

    monkeypatch.setattr(extract, "Client", FakeClient)

    with pytest.raises(ExtractionError, match="invalid structured output"):
        extract_action_items_llm("Write tests", model="test-model")
