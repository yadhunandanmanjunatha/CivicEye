from typing import Literal

from pydantic import BaseModel, Field


class PlannedIncident(BaseModel):
    name: str
    sr_ids: list[str]
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    suggested_resources_text: str


class AdvisoryDraft(BaseModel):
    en: str
    kn: str


class SurgePlan(BaseModel):
    """Surge Commander output."""
    incidents: list[PlannedIncident]
    advisory_draft: AdvisoryDraft
    situation_summary: str
    confidence: float = Field(ge=0, le=1)
