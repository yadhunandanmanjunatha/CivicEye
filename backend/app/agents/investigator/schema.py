from pydantic import BaseModel, Field

from app.core.enums import Agency, Category, Priority


class Referral(BaseModel):
    agency: Agency
    reason: str


class TriageBrief(BaseModel):
    """Case Investigator output. Shown in the officer's System Analysis panel."""
    category: Category
    category_changed: bool = False
    priority: Priority
    department_id: str
    ward_id: str
    suggested_officer_id: str | None = None
    asset_id: str | None = None
    duplicate_of: str | None = None
    duplicate_confidence: float = Field(0, ge=0, le=1)
    repeat_failure: bool = False
    repeat_failure_note: str | None = None
    planned_work_conflict: str | None = None
    interagency_referral: Referral | None = None
    rationale: list[str] = Field(min_length=1, max_length=6)
    confidence: float = Field(ge=0, le=1)
