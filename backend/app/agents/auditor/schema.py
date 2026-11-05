from typing import Literal

from pydantic import BaseModel, Field

from app.core.enums import Verdict

CheckName = Literal["TAKEN_AFTER_ASSIGNMENT", "GPS_WITHIN_RADIUS", "NOT_REUSED", "VISION_FIXED",
                    "VISION_SAME_SCENE"]


class Check(BaseModel):
    name: CheckName
    passed: bool | None  # None = could not be verified / skipped
    detail: str


class AuditVerdict(BaseModel):
    """Evidence Auditor output. Shown in the control room verification queue."""
    verdict: Verdict
    score: int = Field(ge=0, le=100)
    checks: list[Check]
    rationale: list[str] = Field(min_length=1, max_length=6)
    deficiency: str | None = None
