"""Tool: parse_cv

Parses a CV file (PDF, DOCX, or TXT) and stores the result in session state.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from strands import tool

import session
from exceptions import FileSizeError, ParseError, UnsupportedFormatError
from models import ContactInfo, CVSection, ParsedCV, ToolError

_SIZE_LIMIT_MB: float = 10.0
_BYTES_PER_MB: int = 1024 * 1024

_KNOWN_HEADINGS: frozenset[str] = frozenset({
    "summary", "work experience", "education", "skills", "certifications",
    "projects", "experience", "professional experience", "profile", "objective",
})

_RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
_RE_PHONE = re.compile(r"[\+\(]?[0-9][0-9 \-\(\)]{7,}[0-9]")
_RE_LINKEDIN = re.compile(r"linkedin\.com/in/[\w-]+")


@tool
def parse_cv(file_path: str) -> str:
    """Parse a CV file (PDF, DOCX, or TXT) and store the result for later steps.

    Call this first. Pass the path to the CV file.

    Args:
        file_path: Path to the CV file (.pdf, .docx, or .txt).

    Returns:
        A short status message confirming success, or an error description.
    """
    try:
        path = Path(file_path)
        actual_mb = os.path.getsize(path) / _BYTES_PER_MB
        if actual_mb > _SIZE_LIMIT_MB:
            raise FileSizeError(actual_mb)

        ext = path.suffix.lower()
        if ext == ".pdf":
            raw_text = _parse_pdf(path)
        elif ext == ".docx":
            raw_text = _parse_docx(path)
        elif ext == ".txt":
            raw_text = _parse_txt(path)
        else:
            raise UnsupportedFormatError(ext)

        sections = _detect_sections(raw_text)
        contact_info = _extract_contact_info(raw_text)

        session.parsed_cv = ParsedCV(
            raw_text=raw_text,
            sections=sections,
            file_name=path.name,
            contact_info=contact_info,
        )
        return (
            f"CV parsed successfully. Found {len(sections)} sections. "
            f"Contact: {contact_info.name or 'unknown'}. "
            f"Ready for keyword extraction."
        )

    except UnsupportedFormatError as exc:
        return ToolError(
            tool_name="parse_cv",
            error_description=f"Unsupported format '{exc.extension}'. Accepted: .pdf, .docx, .txt.",
            suggested_action="Convert your CV to an accepted format and retry.",
        ).to_json()
    except FileSizeError as exc:
        return ToolError(
            tool_name="parse_cv",
            error_description=f"File size {exc.actual_mb:.1f} MB exceeds the 10 MB limit.",
            suggested_action="Reduce the file size and retry.",
        ).to_json()
    except Exception as exc:
        return ToolError(
            tool_name="parse_cv",
            error_description=f"Could not parse file: {exc}",
            suggested_action="Ensure the file is not corrupted and retry.",
        ).to_json()


def _parse_pdf(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as exc:
        raise ParseError(str(exc)) from exc


def _parse_docx(path: Path) -> str:
    try:
        import docx
        document = docx.Document(str(path))
        return "\n".join(para.text for para in document.paragraphs)
    except Exception as exc:
        raise ParseError(str(exc)) from exc


def _parse_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        raise ParseError(str(exc)) from exc


def _is_section_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.lower() in _KNOWN_HEADINGS:
        return True
    if stripped == stripped.upper() and any(c.isalpha() for c in stripped) and len(stripped) > 1:
        return True
    if stripped.endswith(":") and len(stripped) < 50:
        return True
    return False


def _detect_sections(raw_text: str) -> list[CVSection]:
    lines = raw_text.splitlines()
    sections: list[CVSection] = []
    current_heading: str | None = None
    current_body: list[str] = []

    for line in lines:
        if _is_section_heading(line):
            if current_heading is not None:
                sections.append(CVSection(heading=current_heading, content="\n".join(current_body).strip()))
            elif current_body:
                body = "\n".join(current_body).strip()
                if body:
                    sections.append(CVSection(heading="Header", content=body))
            current_heading = line.strip()
            current_body = []
        else:
            current_body.append(line)

    if current_heading is not None:
        sections.append(CVSection(heading=current_heading, content="\n".join(current_body).strip()))
    elif current_body:
        body = "\n".join(current_body).strip()
        if body:
            sections.append(CVSection(heading="Header", content=body))

    return sections


def _extract_contact_info(raw_text: str) -> ContactInfo:
    lines = raw_text.splitlines()
    header_lines = lines[:10]
    header_block = "\n".join(header_lines)

    email = (m := _RE_EMAIL.search(header_block)) and m.group(0) or None
    phone = (m := _RE_PHONE.search(header_block)) and m.group(0) or None
    linkedin_url = (m := _RE_LINKEDIN.search(header_block)) and m.group(0) or None

    name: str | None = None
    for line in header_lines:
        s = line.strip()
        if not s:
            continue
        if _RE_EMAIL.search(s) or _RE_PHONE.search(s) or _RE_LINKEDIN.search(s):
            continue
        name = s
        break

    return ContactInfo(name=name, email=email, phone=phone, linkedin_url=linkedin_url)
