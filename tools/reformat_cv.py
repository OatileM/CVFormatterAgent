"""Tool: reformat_cv

Validates and stores an ATS-reformatted CV produced by the LLM.
"""

from __future__ import annotations

import re

from strands import tool

import session
from exceptions import ValidationError
from models import CVSection, ReformattedCV, ToolError

_STANDARD_HEADERS = ["Summary", "Work Experience", "Education", "Skills", "Certifications", "Projects"]

_HEADER_PATTERN = re.compile(
    r"^(" + "|".join(re.escape(h) for h in _STANDARD_HEADERS) + r")\s*$",
    re.MULTILINE | re.IGNORECASE,
)


@tool
def reformat_cv(reformatted_cv_text: str) -> str:
    """Store the ATS-reformatted CV produced by the LLM.

    Before calling this tool, YOU must rewrite the CV following these rules:
    - Use ONLY these headers: Summary, Work Experience, Education, Skills,
      Certifications, Projects
    - Single-column plain text, no tables, no pipes, no non-ASCII characters
    - All dates in MM/YYYY format
    - Skills section immediately after Summary
    - Incorporate absent required keywords where experience genuinely supports it
    - Preserve ALL factual information — no fabrication

    Args:
        reformatted_cv_text: The full ATS-optimised CV as plain text.

    Returns:
        A short status message confirming success, or an error description.
    """
    try:
        if not reformatted_cv_text or not reformatted_cv_text.strip():
            raise ValidationError("reformatted_cv_text must not be empty.")

        plain_text = reformatted_cv_text.strip()
        sections = _parse_sections(plain_text)

        session.reformatted_cv = ReformattedCV(
            plain_text=plain_text,
            sections=sections,
        )

        return (
            f"Reformatted CV stored. {len(sections)} sections detected. "
            f"Ready to generate output files."
        )

    except ValidationError as exc:
        return ToolError(
            tool_name="reformat_cv",
            error_description=exc.message,
            suggested_action="Provide the reformatted CV text before calling this tool.",
        ).to_json()
    except Exception as exc:
        return ToolError(
            tool_name="reformat_cv",
            error_description=f"Failed to store reformatted CV: {exc}",
            suggested_action="Ensure reformatted_cv_text is valid plain text.",
        ).to_json()


def _parse_sections(plain_text: str) -> list[CVSection]:
    sections: list[CVSection] = []
    matches = list(_HEADER_PATTERN.finditer(plain_text))

    if not matches:
        if plain_text.strip():
            sections.append(CVSection(heading="", content=plain_text.strip()))
        return sections

    for i, match in enumerate(matches):
        heading = match.group(1)
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(plain_text)
        content = plain_text[content_start:content_end].strip()
        sections.append(CVSection(heading=heading, content=content))

    return sections
