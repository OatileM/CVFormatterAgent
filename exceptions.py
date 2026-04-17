"""Custom exception classes for the CV Formatter Agent.

These exceptions are raised by tools and caught at the tool boundary,
where they are converted into structured ToolError responses.
"""

from __future__ import annotations


class UnsupportedFormatError(Exception):
    """Raised when a CV file has an extension that is not supported.

    Attributes:
        extension: The unsupported file extension (e.g. ".odt").
    """

    def __init__(self, extension: str) -> None:
        self.extension = extension
        accepted = ".pdf, .docx, .txt"
        super().__init__(
            f"Unsupported file format '{extension}'. Accepted formats: {accepted}."
        )


class FileSizeError(Exception):
    """Raised when a CV file exceeds the 10 MB size limit.

    Attributes:
        actual_mb: The actual file size in megabytes.
    """

    LIMIT_MB: float = 10.0

    def __init__(self, actual_mb: float) -> None:
        self.actual_mb = actual_mb
        super().__init__(
            f"File size {actual_mb:.1f} MB exceeds the {self.LIMIT_MB:.0f} MB limit."
        )


class ParseError(Exception):
    """Raised when a CV file cannot be parsed (e.g. corrupted or unreadable).

    Attributes:
        message: Human-readable description of the parse failure.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """Raised when tool input fails validation (e.g. empty job specification).

    Attributes:
        message: Human-readable description of the validation failure.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
