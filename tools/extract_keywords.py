"""Tool: extract_keywords

Validates and stores a keyword list produced by the LLM.
The LLM extracts keywords from the job spec and passes them as a JSON array.
"""

from __future__ import annotations

import json
import re

from strands import tool

import session
from exceptions import ValidationError
from models import Keyword, KeywordList, ToolError


@tool
def extract_keywords(keywords_json: str) -> str:
    """Store the keyword list extracted from the job specification.

    Before calling this tool, YOU must read the job specification and produce
    a JSON array classifying each keyword as required or preferred:
        [{"term": "Python", "classification": "required"}, ...]

    Args:
        keywords_json: JSON array of keyword objects with "term" and
            "classification" ("required" or "preferred") fields.

    Returns:
        A short status message confirming success, or an error description.
    """
    try:
        if not keywords_json or not keywords_json.strip():
            raise ValidationError("keywords_json must not be empty.")

        keyword_list = _parse_keywords(keywords_json.strip())
        session.keyword_list = keyword_list

        req = len(keyword_list.required)
        pref = len(keyword_list.preferred)
        return (
            f"Keywords stored: {req} required, {pref} preferred. "
            f"Ready for keyword analysis."
        )

    except ValidationError as exc:
        return ToolError(
            tool_name="extract_keywords",
            error_description=exc.message,
            suggested_action="Provide a valid JSON array of keyword objects.",
        ).to_json()
    except Exception as exc:
        return ToolError(
            tool_name="extract_keywords",
            error_description=f"Failed to parse keywords: {exc}",
            suggested_action="Ensure keywords_json is a valid JSON array.",
        ).to_json()


def _parse_keywords(keywords_json: str) -> KeywordList:
    cleaned = re.sub(r"```(?:json)?\s*", "", keywords_json, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValidationError(f"No JSON array found in: {keywords_json!r}")

    try:
        raw_items = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc

    keywords: list[Keyword] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        term = str(item.get("term", "")).strip()
        classification = str(item.get("classification", "")).strip().lower()
        if not term:
            continue
        if classification not in ("required", "preferred"):
            classification = "required"
        keywords.append(Keyword(term=term, classification=classification))  # type: ignore[arg-type]

    return KeywordList(keywords=keywords)
