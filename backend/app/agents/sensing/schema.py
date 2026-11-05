from pydantic import BaseModel, Field

from app.core.enums import ClusterDecision


class ClusterOutcome(BaseModel):
    cluster_id: int
    decision: ClusterDecision
    reason: str
    linked_sr: str | None = None
    linked_wo: str | None = None


class SensingReport(BaseModel):
    """Road Hazard Sensing output for one clustering pass."""
    clusters: list[ClusterOutcome] = Field(default_factory=list)
    summary: str
    confidence: float = Field(ge=0, le=1)
