from __future__ import annotations

import logging
import re
from typing import List

from pydantic import RootModel, ValidationError

from ..config import get_settings

logger = logging.getLogger(__name__)

try:
    from ollama import Client
except ImportError:
    Client = None

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
CHECKBOX_PREFIX_PATTERN = re.compile(r"^\s*\[(?:\s*|x|X|todo|TODO)\]\s*")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)
DEFAULT_OLLAMA_MODEL = get_settings().ollama_model


class ActionItemsResponse(RootModel[List[str]]):
    pass


class ExtractionError(RuntimeError):
    pass


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if _is_action_line(line) or _looks_imperative(line):
            extracted.append(_clean_action_item(line))

    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            stripped = sentence.strip()
            if not stripped or not _looks_imperative(stripped):
                continue
            extracted.append(_clean_action_item(stripped))

    return _normalize_action_items(extracted)


def extract_action_items_llm(text: str, model: str = DEFAULT_OLLAMA_MODEL) -> List[str]:
    text = text.strip()
    if not text:
        return []
    if Client is None:
        raise ExtractionError(
            "ollama is not installed. Install it before using extract_action_items_llm."
        )

    settings = get_settings()
    system_prompt = "You extract action items from notes. Return only a JSON array of strings."
    user_prompt = (
        "Read the note and extract all action items or next steps. "
        "Only include tasks that someone still needs to do. "
        "Do not include background information, explanations, or summaries. "
        "Keep each task short and clear. Remove duplicates. "
        "If there are no action items, return [].\n\n"
        f"Note:\n{text}"
    )

    logger.info(
        "Starting Ollama extraction host=%s model=%s system_prompt=%r user_prompt=%r",
        settings.ollama_host,
        model,
        system_prompt,
        user_prompt,
    )

    try:
        client = Client(host=settings.ollama_host)
        response = client.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format=ActionItemsResponse.model_json_schema(),
        )
        logger.info(
            "Completed Ollama extraction host=%s model=%s raw_response=%r",
            settings.ollama_host,
            model,
            response.message.content,
        )
        parsed = ActionItemsResponse.model_validate_json(response.message.content)
        normalized_items = _normalize_action_items(parsed.root)
        logger.info(
            "Normalized Ollama extraction host=%s model=%s items=%r",
            settings.ollama_host,
            model,
            normalized_items,
        )
        return normalized_items
    except ExtractionError:
        raise
    except ValidationError as exc:
        logger.exception(
            "Ollama returned invalid structured output host=%s model=%s",
            settings.ollama_host,
            model,
        )
        raise ExtractionError(
            f"Ollama returned invalid structured output from {settings.ollama_host} "
            f"for model '{model}'. Raw response could not be parsed as a JSON string array."
        ) from exc
    except Exception as exc:
        logger.exception(
            "Ollama extraction failed host=%s model=%s",
            settings.ollama_host,
            model,
        )
        raise ExtractionError(_describe_ollama_failure(exc, settings.ollama_host, model)) from exc


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def _normalize_action_items(items: List[str]) -> List[str]:
    unique: List[str] = []
    seen: set[str] = set()

    for item in items:
        cleaned = _clean_action_item(str(item))
        if not cleaned:
            continue

        lowered = cleaned.lower()
        if lowered in seen:
            continue

        seen.add(lowered)
        unique.append(cleaned)

    return unique


def _clean_action_item(item: str) -> str:
    cleaned = BULLET_PREFIX_PATTERN.sub("", item).strip()
    cleaned = CHECKBOX_PREFIX_PATTERN.sub("", cleaned).strip()
    return cleaned


def _describe_ollama_failure(exc: Exception, host: str, model: str) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    lowered = message.lower()

    if any(token in lowered for token in ("connect", "connection", "refused", "timed out")):
        return (
            f"Could not reach Ollama at {host} for model '{model}'. "
            "Check OLLAMA_HOST and confirm the Ollama service is running. "
            f"Original error: {message}"
        )

    if "not found" in lowered and "model" in lowered:
        return (
            f"Ollama model '{model}' was not found at {host}. "
            "Check OLLAMA_MODEL and pull the model before retrying. "
            f"Original error: {message}"
        )

    return (
        f"Failed to extract action items with Ollama at {host} using model '{model}'. "
        f"Original error: {message}"
    )
