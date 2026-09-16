from typing import Literal

from pydantic import BaseModel, Field


class PolicyCitation(BaseModel):
    chunk_id: str
    page_number: int | None = None
    section: str | None = None
    source: str = "policy.pdf"
    excerpt: str = ""


class ValidationResult(BaseModel):
    status: Literal["PASS", "FAIL"]
    unsupported_claims: list[str] = Field(default_factory=list)


class ClaimDecision(BaseModel):
    case_id: str
    decision: Literal[
        "ADMISSIBLE",
        "ADMISSIBLE_WITH_LIMITS",
        "PARTIALLY_ADMISSIBLE",
        "NOT_ADMISSIBLE",
        "NEEDS_REVIEW",
    ]
    confidence: float
    key_findings: list[str] = Field(default_factory=list)
    applicable_limits: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    citations: list[PolicyCitation] = Field(default_factory=list)
    validation: ValidationResult
    trace: list[dict] = Field(default_factory=list)