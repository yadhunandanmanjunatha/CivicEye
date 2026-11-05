from typing import Any

from fastapi import APIRouter, Depends

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.schemas import ERROR_RESPONSES, Page

router = APIRouter(tags=["control room"], responses=ERROR_RESPONSES)


@router.get("/agent-runs", response_model=Page[s.AgentRunRow], dependencies=[Depends(fx.stub)])
def agent_runs(agent: str | None = None, status: str | None = None, model: str | None = None,
               overridden: bool | None = None, sr_id: str | None = None, page: int = 1, page_size: int = 10,
               format: str | None = None):
    return Page(items=[fx.run_row()], total=1, page=page, page_size=page_size)


@router.get("/agent-runs/{run_id}", response_model=s.AgentRunDetail, dependencies=[Depends(fx.stub)])
def agent_run(run_id: str):
    return fx.run_detail()


@router.get("/incidents", response_model=list[s.IncidentOut], dependencies=[Depends(fx.stub)])
def incidents(status: str | None = None):
    return [fx.incident()]


@router.get("/incidents/{incident_id}", response_model=s.IncidentDetail, dependencies=[Depends(fx.stub)])
def incident(incident_id: str):
    return s.IncidentDetail(**fx.incident().model_dump(), complaints=[fx.row()])


@router.post("/incidents/{incident_id}/advisory/publish", response_model=s.IncidentOut,
             dependencies=[Depends(fx.stub)])
def publish(incident_id: str, body: s.PublishIn):
    return fx.incident()


@router.get("/hazards/clusters", response_model=dict[str, Any], dependencies=[Depends(fx.stub)])
def clusters(bbox: str | None = None, status: str | None = None):
    """GeoJSON FeatureCollection of hazard clusters."""
    return fx.feature_collection()


@router.get("/hazards/detections", response_model=dict[str, Any], dependencies=[Depends(fx.stub)])
def detections(bbox: str | None = None, since: str | None = None):
    """GeoJSON FeatureCollection of raw detections (points)."""
    return fx.feature_collection()


@router.get("/hazards/review-queue", response_model=list[s.ReviewItemOut], dependencies=[Depends(fx.stub)])
def review_queue():
    return [s.ReviewItemOut(id=1, cluster_id=3, reason="Only 2 vehicles; low confidence 0.55", status="OPEN",
                            centre=s.LatLon(lat=12.91, lon=77.49), distinct_vehicles=2, avg_confidence=0.55,
                            created_at=fx.NOW)]


@router.post("/hazards/review/{cluster_id}", response_model=s.ClusterDecisionOut, dependencies=[Depends(fx.stub)])
def review_decide(cluster_id: int, body: s.ReviewDecisionIn):
    return s.ClusterDecisionOut(decision=body.decision, reason=body.reason)


@router.get("/data-sources", response_model=list[s.DataSourceOut], dependencies=[Depends(fx.stub)])
def data_sources():
    return [s.DataSourceOut(id="oem-sim", name="Connected-vehicle feed (simulated partner)", kind="VEHICLE",
                            last_ingest_at=fx.NOW, accepted_24h=1240, rejected_24h=31)]


@router.get("/data-sources/{source_id}/rejections", response_model=Page[s.RejectionOut],
            dependencies=[Depends(fx.stub)])
def rejections(source_id: str, page: int = 1, page_size: int = 10, format: str | None = None):
    r = s.RejectionOut(id=1, source_record_id="oem-sim-000999", reason="OUT_OF_BOUNDS", detail="lat 13.4",
                       at=fx.NOW)
    return Page(items=[r], total=1, page=page, page_size=page_size)


@router.get("/kpi", response_model=s.Kpi, dependencies=[Depends(fx.stub)])
def kpi():
    return fx.kpi()


def _notif() -> s.NotificationOut:
    return s.NotificationOut(id=1, event="complaint.acknowledged", title="Grievance SR-2026-000123 received",
                             body="We have received your grievance.", language="en", channel="IN_APP",
                             related_sr_id="SR-2026-000123", sent_by="case_investigator", read=False,
                             created_at=fx.NOW)


@router.get("/notifications", response_model=Page[s.NotificationOut], dependencies=[Depends(fx.stub)])
def outbox(page: int = 1, page_size: int = 10, format: str | None = None):
    return Page(items=[_notif()], total=1, page=page, page_size=page_size)


@router.get("/notifications/mine", response_model=Page[s.NotificationOut], dependencies=[Depends(fx.stub)])
def my_notifications(page: int = 1, page_size: int = 10):
    return Page(items=[_notif()], total=1, page=page, page_size=page_size)


@router.post("/notifications/{notification_id}/read", response_model=s.NotificationOut,
             dependencies=[Depends(fx.stub)])
def mark_read(notification_id: int):
    return _notif()
