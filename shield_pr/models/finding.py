"""Finding model representing a single review finding."""

from typing import Literal
from pydantic import BaseModel, Field


class Finding(BaseModel):
    """Represents a single code review finding.

    Attributes:
        severity: Finding severity level (HIGH, MEDIUM, LOW)
        category: Finding category (security, performance, etc.)
        file_path: Path to file containing the issue
        line_number: Optional line number where issue occurs
        description: Detailed description of the finding
        suggestion: Suggested fix or improvement
        code_snippet: Optional code snippet showing the issue
    """

    severity: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description="Severity level of the finding"
    )
    category: str = Field(
        description="Category of the finding (security, performance, maintainability, etc.)"
    )
    file_path: str = Field(
        description="Path to the file containing the issue"
    )
    line_number: int | None = Field(
        default=None,
        description="Line number where the issue occurs"
    )
    description: str = Field(
        description="Detailed description of the finding"
    )
    suggestion: str | None = Field(
        default="",
        description="Suggested fix or improvement"
    )
    code_snippet: str | None = Field(
        default=None,
        description="Code snippet showing the issue"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "severity": "HIGH",
                "category": "security",
                "file_path": "app/auth.py",
                "line_number": 42,
                "description": "SQL injection vulnerability detected",
                "suggestion": "Use parameterized queries instead of string concatenation",
                "code_snippet": "query = f\"SELECT * FROM users WHERE id = {user_id}\""
            }
        }
