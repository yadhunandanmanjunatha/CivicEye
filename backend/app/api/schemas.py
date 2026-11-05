"""Request/response models for every endpoint (CONTRACTS §3–§5). This file IS the API contract:
Lane B generates web/src/api/types.ts from the OpenAPI built from it."""
from datetime import datetime
from typing import Any, Literal
import uuid

from pydantic import Field, field_validator

from app.agents.auditor.schema import AuditVerdict
from app.agents.investigator.schema import TriageBrief
from app.core.enums import (
    ActorType, Agency, AgencyStatus, AgentName, AttachmentKind, Category, ClusterDecision, HoldReason,
    Language, Priority, ProposalStatus, RejectReason, Role, RunStatus, SLAState, Source, SRStatus,
    Verdict, WOStatus,
)
from app.core.schemas import LatLon, Schema

# ---------------------------------------------------------------- auth / users


class RegisterIn(Schema):
    name: str = Field(min_length=2, max_length=120)
    mobile: str = Field(pattern=r"^[6-9]\d{9}$", description="10-digit Indian mobile number")
    password: str = Field(min_length=8, max_length=128)
    language: Language = Language.EN


class LoginIn(Schema):
    mobile: str = Field(pattern=r"^\d{10}$")
    password: str


class UserOut(Schema):
    id: uuid.UUID
    name: str
    mobile_masked: str
    role: Role
    designation: str | None = None
    ward_id: str | None = None
    department_id: str | None = None
    crew_id: str | None = None
    agency: Agency | None = None
    language: Language = Language.EN


class StaffIn(Schema):
    name: str = Field(min_length=2, max_length=120)
    mobile: str = Field(pattern=r"^[6-9]\d{9}$")
    password: str = Field(min_length=8)
    role: Literal["WARD_OFFICER", "FIELD_TEAM", "CONTROL_ROOM", "AGENCY"]
    designation: str | None = None
    ward_id: str | None = None
    department_id: str | None = None
    crew_id: str | None = None
    agency: Agency | None = None
    office_phone: str | None = None


class StaffPatch(Schema):
    name: str | None = None
    designation: str | None = None
    ward_id: str | None = None
    department_id: str | None = None
    crew_id: str | None = None
    agency: Agency | None = None
    office_phone: str | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8)


class StaffOut(UserOut):
    is_active: bool
    office_phone: str | None = None
    created_at: datetime


class CaptchaOut(Schema):
    captcha_id: uuid.UUID
    question: str


# ---------------------------------------------------------------- public


class PublicStats(Schema):
    total: int
    resolved: int
    within_sla_pct: float
    avg_resolution_days: float
    unique_issues: int


class TickerItem(Schema):
    id: str
    text_en: str
    text_kn: str | None = None
    published_at: datetime


class WardDirectoryEntry(Schema):
    id: str
    name: str
    name_kn: str | None = None
    zone: str
    officer_name: str | None = None
    officer_designation: str | None = None
    office_phone: str | None = None


class SearchHit(Schema):
    title: str
    path: str


class GrievanceHit(Schema):
    sr_id: str
    category: Category
    status: SRStatus


class SearchResult(Schema):
    grievances: list[GrievanceHit]
    pages: list[SearchHit]
    wards: list[WardDirectoryEntry]


class VisitIn(Schema):
    session_key: str = Field(min_length=8, max_length=64)


class VisitCount(Schema):
    count: int


class CategoryOut(Schema):
    id: Category
    name_en: str
    name_kn: str
    department_id: str


class DepartmentOut(Schema):
    id: str
    name: str
    name_kn: str | None = None


class WardOut(Schema):
    id: str
    name: str
    name_kn: str | None = None
    zone: str
    geojson: dict[str, Any] | None = None


class CrewOut(Schema):
    id: str
    name: str
    ward_id: str
    skills: list[str]
    capacity: int
    open_work_orders: int


# ---------------------------------------------------------------- complaints


class AckSlip(Schema):
    sr_id: str
    tracking_code: str
    created_at: datetime
    category: Category
    ward_name: str | None
    department_name: str | None
    expected_resolution_at: datetime | None
    language: Language


class Attachment(Schema):
    id: uuid.UUID
    kind: AttachmentKind
    url: str
    taken_at: datetime | None = None
    uploaded_at: datetime


class TimelineEntry(Schema):
    at: datetime
    stage: str
    remarks: str
    actor_type: ActorType


class TrackPhotos(Schema):
    before: Attachment | None = None
    after: Attachment | None = None


class TrackView(Schema):
    sr_id: str
    category: Category
    status: SRStatus
    priority: Priority
    ward_name: str | None
    created_at: datetime
    expected_resolution_at: datetime | None
    timeline: list[TimelineEntry]
    photos: TrackPhotos
    can_confirm: bool
    can_reopen: bool
    delay_reason: str | None = None
    reporter_count: int = 1
    incident_name: str | None = None


class ConfirmIn(Schema):
    tracking_code: str | None = None
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)


class ReopenIn(Schema):
    tracking_code: str | None = None
    reason: str = Field(min_length=5, max_length=1000)


class ComplaintRow(Schema):
    sr_id: str
    category: Category
    priority: Priority
    status: SRStatus
    ward_id: str | None
    address: str | None
    created_at: datetime
    owner_name: str | None
    sla_state: SLAState | None
    sla_due_at: datetime | None
    sla_remaining_s: int | None
    escalation_level: int
    reporter_count: int
    source: Source


class WorkOrderRow(Schema):
    wo_id: str
    sr_id: str
    crew_id: str
    status: WOStatus
    scope: str
    assigned_at: datetime
    completed_at: datetime | None = None
    audit_verdict: Verdict | None = None


class ReferralOut(Schema):
    id: str
    sr_id: str
    agency: Agency
    reason: str
    sent_at: datetime
    followups_sent: int
    last_followup_at: datetime | None
    agency_status: AgencyStatus
    agency_reply: str | None
    replied_at: datetime | None
    messages: list[dict[str, Any]] = []


class ReporterContact(Schema):
    name: str | None
    mobile: str | None


class ComplaintDetail(ComplaintRow):
    description: str
    location: LatLon
    landmark: str | None = None
    department_id: str | None = None
    asset_id: str | None = None
    parent_sr_id: str | None = None
    incident_id: str | None = None
    corroboration_count: int = 0
    attachments: list[Attachment]
    work_orders: list[WorkOrderRow]
    referrals: list[ReferralOut]
    timeline: list[TimelineEntry]
    reporter_contact: ReporterContact | None = None


class OverrideChanges(Schema):
    category: Category | None = None
    priority: Priority | None = None
    department_id: str | None = None
    owner_id: uuid.UUID | None = None


class AcceptIn(Schema):
    run_id: uuid.UUID


class OverrideIn(Schema):
    run_id: uuid.UUID
    changes: OverrideChanges
    reason: str = Field(min_length=5)


class MergeIn(Schema):
    parent_sr_id: str
    reason: str = Field(min_length=3)


class ReasonIn(Schema):
    reason: str = Field(min_length=3)


class RejectIn(Schema):
    reason_code: RejectReason
    explanation: str = Field(min_length=10, description="Shown to the citizen")


class HoldIn(Schema):
    reason_code: HoldReason
    note: str = Field(min_length=3)


# ---------------------------------------------------------------- agent runs


class AgentStep(Schema):
    seq: int
    tool: str
    args: dict[str, Any]
    result_summary: Any = None
    ok: bool
    ms: int


class AgentRunRow(Schema):
    id: uuid.UUID
    agent: AgentName
    trigger: str
    subject_id: str | None
    status: RunStatus
    model: str | None
    decision_summary: str | None
    confidence: float | None
    latency_ms: int | None
    overridden: bool
    started_at: datetime


class AgentRunDetail(AgentRunRow):
    input_summary: dict[str, Any]
    output: dict[str, Any] | None
    rationale: list[str] | None
    fallback_reason: str | None = None
    overridden_by: uuid.UUID | None = None
    override_reason: str | None = None
    steps: list[AgentStep]


class DuplicateSuggestion(Schema):
    sr_id: str
    confidence: float
    distance_m: float
    status: SRStatus


class AnalysisView(Schema):
    run: AgentRunDetail | None
    brief: TriageBrief | None
    duplicate_suggestions: list[DuplicateSuggestion]
    in_progress: bool = False


# ---------------------------------------------------------------- work orders


class WorkOrderIn(Schema):
    crew_id: str
    asset_id: str | None = None
    root_cause: str = Field(min_length=3)
    scope: str = Field(min_length=3)
    est_cost_inr: float = Field(ge=0)


class WorkOrderDetail(WorkOrderRow):
    asset_id: str | None = None
    root_cause: str | None
    est_cost_inr: float | None
    started_at: datetime | None = None
    rework_reason: str | None = None
    quality_flag: str | None = None
    complaint_category: Category
    complaint_description: str
    complaint_location: LatLon
    complaint_address: str | None = None
    photos: list[Attachment]
    audit: AuditVerdict | None = None


class VerificationItem(Schema):
    wo_id: str
    sr_id: str
    crew_id: str
    category: Category
    completed_at: datetime | None
    before: Attachment | None
    after: Attachment | None
    audit: AuditVerdict | None
    audit_pending: bool


# ---------------------------------------------------------------- follow-up


class ProposalOut(Schema):
    id: int
    wo_id: str
    sr_id: str
    from_crew_id: str
    to_crew_id: str
    reason: str
    evidence: dict[str, Any]
    status: ProposalStatus
    created_at: datetime


class AgencyReplyIn(Schema):
    agency_status: Literal["ACKNOWLEDGED", "IN_PROGRESS", "RESOLVED", "NOT_OURS"]
    message: str = Field(min_length=3, max_length=2000)


class AgencyReferral(ReferralOut):
    category: Category
    description: str
    location: LatLon
    address: str | None
    asset_id: str | None


class EscalationOut(Schema):
    id: int
    sr_id: str
    level: int
    trigger: str
    reason_summary: str
    authority_name: str | None
    authority_designation: str | None
    created_at: datetime
    deadline: datetime | None


class InventoryOut(Schema):
    item: str
    name: str
    unit: str
    qty: float
    out_of_stock_since: datetime | None


class MaterialRequestOut(Schema):
    id: int
    item: str
    qty: float
    sr_id: str | None
    reason: str
    status: str
    raised_by: str
    created_at: datetime


# ---------------------------------------------------------------- control room


class IncidentOut(Schema):
    id: str
    name: str
    severity: str
    status: str
    report_count: int
    centre: LatLon | None
    suggested_resources: str | None
    advisory_draft_en: str | None
    advisory_draft_kn: str | None
    advisory_published: bool
    published_at: datetime | None
    summary: str | None
    summary_at: datetime | None
    created_at: datetime


class IncidentDetail(IncidentOut):
    complaints: list[ComplaintRow]


class PublishIn(Schema):
    text_en: str = Field(min_length=10, max_length=500)
    text_kn: str | None = Field(None, max_length=800)


class ReviewItemOut(Schema):
    id: int
    cluster_id: int
    reason: str
    status: str
    centre: LatLon
    distinct_vehicles: int
    avg_confidence: float
    created_at: datetime


class ReviewDecisionIn(Schema):
    decision: Literal["CREATE", "DISMISS"]
    reason: str = Field(min_length=3)


class DataSourceOut(Schema):
    id: str
    name: str
    kind: str
    last_ingest_at: datetime | None
    accepted_24h: int
    rejected_24h: int


class RejectionOut(Schema):
    id: int
    source_record_id: str | None
    reason: str
    detail: str | None
    at: datetime


class CountBy(Schema):
    key: str
    count: int


class Kpi(Schema):
    total_reports: int
    unique_issues: int
    sla_compliance_pct: float
    reopen_rate_pct: float
    closed_citizen: int
    closed_auto: int
    open_now: int
    breached_now: int
    avg_rating: float | None
    by_category: list[CountBy]
    by_ward: list[CountBy]
    by_source: list[CountBy]


class NotificationOut(Schema):
    id: int
    event: str
    title: str
    body: str
    language: Language
    channel: str
    related_sr_id: str | None
    sent_by: str
    read: bool
    created_at: datetime
    recipient: str | None = None  # masked; only in the Control Room outbox


# ---------------------------------------------------------------- ingestion


class DetectionIn(Schema):
    source_record_id: str = Field(min_length=1, max_length=80)
    lat: float
    lon: float
    hazard_type: str
    detected_at: datetime
    confidence: float | None = 0.5
    speed_kmph: float | None = None
    vertical_accel_peak_g: float | None = None
    vehicle_ref: str = Field(min_length=1, max_length=80)
    image_url: str | None = None

    model_config = Schema.model_config | {"extra": "allow"}  # extra fields are checked, then rejected


class DetectionBatch(Schema):
    records: list[dict[str, Any]] = Field(max_length=1000)


class IngestRejection(Schema):
    source_record_id: str | None
    reason: str
    detail: str | None = None


class IngestResult(Schema):
    accepted: int
    rejected: int
    duplicates: int
    rejections: list[IngestRejection]


class WeatherAlertIn(Schema):
    source_alert_id: str
    area_name: str
    lat: float
    lon: float
    radius_km: float = Field(gt=0, le=50)
    severity: Literal["YELLOW", "ORANGE", "RED"]
    kind: Literal["HEAVY_RAIN"] = "HEAVY_RAIN"
    valid_from: datetime
    valid_to: datetime

    @field_validator("valid_to")
    @classmethod
    def _after(cls, v, info):
        if "valid_from" in info.data and v <= info.data["valid_from"]:
            raise ValueError("valid_to must be after valid_from")
        return v


class ClusterDecisionOut(Schema):
    decision: ClusterDecision
    reason: str
