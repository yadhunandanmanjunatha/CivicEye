from typing import Literal

from pydantic import BaseModel, Field

from app.core.enums import SLAState


class Cause(BaseModel):
    type: Literal["CREW_OVERLOAD", "NO_STOCK", "AGENCY_PENDING", "UNASSIGNED", "OTHER"]
    evidence: str


class FollowupDecision(BaseModel):
    """Follow-up & Escalation output for one case."""
    case_id: str
    sla_state: SLAState
    diagnosed_causes: list[Cause] = Field(default_factory=list)
    actions_taken: list[str] = Field(default_factory=list)
    proposals: list[int] = Field(default_factory=list)
    citizen_message_reason: str | None = None
    rationale: list[str] = Field(min_length=1, max_length=6)
    confidence: float = Field(ge=0, le=1)
