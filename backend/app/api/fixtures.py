"""Correctly shaped sample payloads used ONLY by endpoints still marked with the X-Stub header.
Each endpoint drops its stub when it is implemented (see TASKS.md A06–A19). Never rendered as real data."""
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import Response

from app.agents.auditor.schema import AuditVerdict, Check
from app.agents.investigator.schema import TriageBrief
from app.api import schemas as s

NOW = datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc)
UID = uuid.UUID("00000000-0000-0000-0000-000000000001")
RUN = uuid.UUID("00000000-0000-0000-0000-0000000000a1")


def stub(response: Response) -> None:
    """FastAPI dependency: marks a response as coming from a contract stub."""
    response.headers["X-Stub"] = "true"


def user(role="WARD_OFFICER") -> s.UserOut:
    return s.UserOut(id=UID, name="Example Officer", mobile_masked="98XXXXXX10", role=role,
                     designation="Assistant Engineer", ward_id="W12", department_id="ROADS")


def attachment(kind="CITIZEN") -> s.Attachment:
    return s.Attachment(id=uuid.uuid4(), kind=kind, url="/api/v1/media/example-token", taken_at=NOW,
                        uploaded_at=NOW)


def timeline() -> list[s.TimelineEntry]:
    return [
        s.TimelineEntry(at=NOW, stage="SUBMITTED", remarks="Grievance received.", actor_type="SYSTEM"),
        s.TimelineEntry(at=NOW + timedelta(minutes=1), stage="SUBMITTED",
                        remarks="System linked your complaint with 2 similar reports.", actor_type="AGENT"),
    ]


def row(sr_id="SR-2026-000123") -> s.ComplaintRow:
    return s.ComplaintRow(sr_id=sr_id, category="POTHOLE", priority="P2", status="SUBMITTED", ward_id="W12",
                          address="Near Govt. Higher Primary School, Kengeri", created_at=NOW,
                          owner_name="Example Officer", sla_state="ON_TRACK",
                          sla_due_at=NOW + timedelta(days=5), sla_remaining_s=432000, escalation_level=0,
                          reporter_count=3, source="CITIZEN_WEB")


def wo_row() -> s.WorkOrderRow:
    return s.WorkOrderRow(wo_id="WO-2026-000041", sr_id="SR-2026-000123", crew_id="W12-A", status="ASSIGNED",
                          scope="Fill pothole with cold-mix asphalt", assigned_at=NOW)


def referral() -> s.ReferralOut:
    return s.ReferralOut(id="REF-2026-000001", sr_id="SR-2026-000124", agency="BESCOM",
                         reason="Feeder fault suspected", sent_at=NOW, followups_sent=1, last_followup_at=NOW,
                         agency_status="PENDING", agency_reply=None, replied_at=None,
                         messages=[{"at": NOW.isoformat(), "from": "CivicFlow", "text": "Follow-up 1"}])


def detail() -> s.ComplaintDetail:
    return s.ComplaintDetail(**row().model_dump(), description="Large pothole near the school gate.",
                             location=s.LatLon(lat=12.9081, lon=77.4874), landmark="School gate",
                             department_id="ROADS", attachments=[attachment()], work_orders=[wo_row()],
                             referrals=[], timeline=timeline(),
                             reporter_contact=s.ReporterContact(name="Citizen", mobile="98XXXXXX21"))


def brief() -> TriageBrief:
    return TriageBrief(category="POTHOLE", priority="P2", department_id="ROADS", ward_id="W12",
                       suggested_officer_id=str(UID), duplicate_of=None, duplicate_confidence=0.0,
                       rationale=["Pothole on a local road 40 m from a school.",
                                  "3 citizens reported the same spot.",
                                  "No planned works nearby."], confidence=0.86)


def step(seq=1) -> s.AgentStep:
    return s.AgentStep(seq=seq, tool="get_sensitive_places_nearby", args={"lat": 12.9081, "lon": 77.4874,
                       "radius_m": 200}, result_summary=[{"name": "Govt. Higher Primary School", "m": 40}],
                       ok=True, ms=12)


def run_row() -> s.AgentRunRow:
    return s.AgentRunRow(id=RUN, agent="case_investigator", trigger="complaint.submitted",
                         subject_id="SR-2026-000123", status="SUCCEEDED", model="rules",
                         decision_summary="P2 · Roads · Ward 12", confidence=0.86, latency_ms=840,
                         overridden=False, started_at=NOW)


def run_detail() -> s.AgentRunDetail:
    return s.AgentRunDetail(**run_row().model_dump(), input_summary={"sr_id": "SR-2026-000123"},
                            output=brief().model_dump(mode="json"), rationale=brief().rationale,
                            steps=[step(1), step(2)])


def audit() -> AuditVerdict:
    return AuditVerdict(verdict="FAIL", score=20, checks=[
        Check(name="TAKEN_AFTER_ASSIGNMENT", passed=True, detail="Taken 3 h after assignment"),
        Check(name="GPS_WITHIN_RADIUS", passed=False, detail="Photo taken 2.1 km from the complaint (limit 50 m)"),
        Check(name="NOT_REUSED", passed=True, detail="No similar photo found"),
        Check(name="VISION_FIXED", passed=None, detail="Skipped: no vision model configured"),
        Check(name="VISION_SAME_SCENE", passed=None, detail="Skipped: no vision model configured"),
    ], rationale=["Location check failed by a wide margin."], deficiency="After-photo is 2.1 km away.")


def wo_detail() -> s.WorkOrderDetail:
    return s.WorkOrderDetail(**wo_row().model_dump(), root_cause="Water seepage", est_cost_inr=4500,
                             complaint_category="POTHOLE", complaint_description="Large pothole",
                             complaint_location=s.LatLon(lat=12.9081, lon=77.4874),
                             photos=[attachment("BEFORE")], audit=None)


def incident() -> s.IncidentOut:
    return s.IncidentOut(id="INC-2026-0001", name="Kengeri Underpass Waterlogging", severity="HIGH",
                         status="ACTIVE", report_count=17, centre=s.LatLon(lat=12.912, lon=77.485),
                         suggested_resources="2 jetting machines", advisory_draft_en="Avoid Kengeri underpass.",
                         advisory_draft_kn=None, advisory_published=False, published_at=None,
                         summary="17 reports in 40 minutes.", summary_at=NOW, created_at=NOW)


def kpi() -> s.Kpi:
    return s.Kpi(total_reports=245, unique_issues=198, sla_compliance_pct=81.5, reopen_rate_pct=7.9,
                 closed_citizen=120, closed_auto=31, open_now=47, breached_now=6, avg_rating=4.1,
                 by_category=[s.CountBy(key="POTHOLE", count=80)], by_ward=[s.CountBy(key="W12", count=60)],
                 by_source=[s.CountBy(key="CITIZEN_WEB", count=230)])


def feature_collection() -> dict:
    return {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [77.4874, 12.9081]},
         "properties": {"cluster_id": 1, "distinct_vehicles": 7, "status": "ACTIONED", "decision": "CORROBORATE"}}]}
