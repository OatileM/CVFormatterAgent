"""Shared session state for the CV Formatter Agent.

Tools store their outputs here so the LLM never needs to pass large JSON
strings as tool arguments — it only passes simple keys like 'cv_path'.
"""

from __future__ import annotations

from models import KeywordList, KeywordReport, ParsedCV, ReformattedCV

# ---------------------------------------------------------------------------
# Single shared session — one run at a time
# ---------------------------------------------------------------------------

parsed_cv: ParsedCV | None = None
keyword_list: KeywordList | None = None
keyword_report: KeywordReport | None = None
reformatted_cv: ReformattedCV | None = None


def reset() -> None:
    """Clear all session state (call before each new run)."""
    global parsed_cv, keyword_list, keyword_report, reformatted_cv
    parsed_cv = None
    keyword_list = None
    keyword_report = None
    reformatted_cv = None
