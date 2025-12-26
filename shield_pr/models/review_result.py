"""Review result model representing complete review output."""

from typing import List
from pydantic import BaseModel, Field
from shield_pr.models.finding import Finding


class ReviewResult(BaseModel):
    """Represents complete review results for a code file.

    Attributes:
        platform: Platform detected for the code (android, ios, etc.)
        findings: List of findings discovered during review
        summary: High-level summary of the review
        confidence: Confidence score for the review (0.0-1.0)
    """

    platform: str = Field(
        description="Platform detected for the code"
    )
    findings: List[Finding] = Field(
        default_factory=list,
        description="List of findings discovered during review"
    )
    summary: str = Field(
        description="High-level summary of the review"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score for the review (0.0-1.0)"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "platform": "android",
                "findings": [
                    {
                        "severity": "HIGH",
                        "category": "memory-leak",
                        "file_path": "MainActivity.kt",
                        "line_number": 25,
                        "description": "Activity context leaked through listener",
                        "suggestion": "Use WeakReference or remove listener in onDestroy",
                        "code_snippet": "listener.setContext(this)"
                    }
                ],
                "summary": "Found 1 high severity issue related to memory management",
                "confidence": 0.95
            }
        }
