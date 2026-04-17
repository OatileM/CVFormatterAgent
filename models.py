"""Shared data models for the CV Formatter Agent.

All models are implemented as Python dataclasses and are JSON-serialisable,
as required by the Strands Agents SDK tool interface.
"""

from __future__ import annotations

import dataclasses
import json
from typing import Literal


@dataclasses.dataclass
class CVSection:
    """A single labelled section extracted from a CV."""

    heading: str  # e.g. "Work Experience"
    content: str  # Raw text of the section body

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ContactInfo:
    """Contact details extracted from the CV header block."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ParsedCV:
    """Structured representation of a parsed CV file."""

    raw_text: str                    # Full extracted text
    sections: list[CVSection]        # Ordered list of identified sections
    file_name: str                   # Original file name (for output naming)
    contact_info: ContactInfo        # Extracted header block

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "sections": [s.to_dict() for s in self.sections],
            "file_name": self.file_name,
            "contact_info": self.contact_info.to_dict(),
        }


@dataclasses.dataclass
class Keyword:
    """A keyword extracted from a job specification."""

    term: str
    classification: Literal["required", "preferred"]

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class KeywordList:
    """A collection of classified keywords extracted from a job specification."""

    keywords: list[Keyword]

    @property
    def required(self) -> list[Keyword]:
        """Return only keywords classified as required."""
        return [kw for kw in self.keywords if kw.classification == "required"]

    @property
    def preferred(self) -> list[Keyword]:
        """Return only keywords classified as preferred."""
        return [kw for kw in self.keywords if kw.classification == "preferred"]

    def to_dict(self) -> dict:
        return {"keywords": [kw.to_dict() for kw in self.keywords]}


@dataclasses.dataclass
class KeywordReport:
    """Results of the ATS keyword gap analysis."""

    present_required: list[str]   # Required keywords found in CV
    absent_required: list[str]    # Required keywords missing from CV
    present_preferred: list[str]  # Preferred keywords found in CV
    absent_preferred: list[str]   # Preferred keywords missing from CV
    ats_score: float              # 0.0–100.0, based on required keywords only

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ReformattedCV:
    """ATS-optimised CV produced by the reformat_cv tool."""

    plain_text: str              # Full ATS-optimised CV as plain text
    sections: list[CVSection]    # Structured sections for DOCX generation

    def to_dict(self) -> dict:
        return {
            "plain_text": self.plain_text,
            "sections": [s.to_dict() for s in self.sections],
        }


@dataclasses.dataclass
class OutputPaths:
    """Paths to the generated output files."""

    txt_path: str
    docx_path: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ToolError:
    """Structured error response returned by any tool on failure."""

    tool_name: str
    error_description: str
    suggested_action: str

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dict representation of this error."""
        return {
            "tool_name": self.tool_name,
            "error_description": self.error_description,
            "suggested_action": self.suggested_action,
        }

    def to_json(self) -> str:
        """Return a JSON string representation of this error."""
        return json.dumps(self.to_dict())
