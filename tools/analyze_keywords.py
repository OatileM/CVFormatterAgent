"""Tool: analyze_keywords

Performs deterministic ATS keyword gap analysis using session state.
"""

from __future__ import annotations

from strands import tool

import session
from models import KeywordReport, ToolError


@tool
def analyze_keywords() -> str:
    """Compare the parsed CV against the extracted keywords and compute ATS score.

    Call this after parse_cv and extract_keywords have both completed.
    No arguments needed — reads from session state.

    Returns:
        A short status message with the ATS score, or an error description.
    """
    try:
        if session.parsed_cv is None:
            return ToolError(
                tool_name="analyze_keywords",
                error_description="No parsed CV found. Call parse_cv first.",
                suggested_action="Call parse_cv before analyze_keywords.",
            ).to_json()

        if session.keyword_list is None:
            return ToolError(
                tool_name="analyze_keywords",
                error_description="No keyword list found. Call extract_keywords first.",
                suggested_action="Call extract_keywords before analyze_keywords.",
            ).to_json()

        raw_text_lower = session.parsed_cv.raw_text.lower()

        present_required: list[str] = []
        absent_required: list[str] = []
        present_preferred: list[str] = []
        absent_preferred: list[str] = []

        for kw in session.keyword_list.required:
            if kw.term.lower() in raw_text_lower:
                present_required.append(kw.term)
            else:
                absent_required.append(kw.term)

        for kw in session.keyword_list.preferred:
            if kw.term.lower() in raw_text_lower:
                present_preferred.append(kw.term)
            else:
                absent_preferred.append(kw.term)

        total_required = len(present_required) + len(absent_required)
        ats_score = round((len(present_required) / total_required) * 100, 1) if total_required > 0 else 0.0

        session.keyword_report = KeywordReport(
            present_required=present_required,
            absent_required=absent_required,
            present_preferred=present_preferred,
            absent_preferred=absent_preferred,
            ats_score=ats_score,
        )

        return (
            f"ATS analysis complete. Score: {ats_score}%. "
            f"Required present: {len(present_required)}/{total_required}. "
            f"Ready for CV reformatting."
        )

    except Exception as exc:
        return ToolError(
            tool_name="analyze_keywords",
            error_description=f"Failed to analyze keywords: {exc}",
            suggested_action="Ensure parse_cv and extract_keywords completed successfully.",
        ).to_json()
