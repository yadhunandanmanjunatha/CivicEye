from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.enums import Category, Language
from app.core.schemas import ERROR_RESPONSES, ImportResult, Ok, Page

router = APIRouter(prefix="/complaints", tags=["complaints"], responses=ERROR_RESPONSES)


@router.post("", response_model=s.AckSlip, status_code=201, dependencies=[Depends(fx.stub)])
def lodge(
    category: Category = Form(...), description: str = Form(..., min_length=10, max_length=2000),
    lat: float = Form(...), lon: float = Form(...), address: str | None = Form(None),
    landmark: str | None = Form(None), name: str | None = Form(None), mobile: str | None = Form(None),
    anonymous: bool = Form(False), language: Language = Form(Language.EN),
    captcha_id: str = Form(...), captcha_answer: int = Form(...), consent: bool = Form(...),
    photo: UploadFile | None = File(None),
):
    return s.AckSlip(sr_id="SR-2026-000123", tracking_code="K7Q2-MX9P", created_at=fx.NOW, category=category,
                     ward_name="Kengeri", department_name="Roads & Infrastructure",
                     expected_resolution_at=fx.NOW, language=language)


@router.get("/track", response_model=s.TrackView, dependencies=[Depends(fx.stub)])
def track(sr_id: str, tracking_code: str | None = None):
    return s.TrackView(sr_id=sr_id, category="POTHOLE", status="RESOLVED", priority="P2", ward_name="Kengeri",
                       created_at=fx.NOW, expected_resolution_at=fx.NOW, timeline=fx.timeline(),
                       photos=s.TrackPhotos(before=fx.attachment("BEFORE"), after=fx.attachment("AFTER")),
                       can_confirm=True, can_reopen=True, reporter_count=3)


@router.get("/mine", response_model=Page[s.ComplaintRow], dependencies=[Depends(fx.stub)])
def mine(page: int = 1, page_size: int = 10):
    return Page(items=[fx.row()], total=1, page=page, page_size=page_size)


@router.post("/import", response_model=ImportResult, dependencies=[Depends(fx.stub)])
def import_csv(file: UploadFile = File(...)):
    return ImportResult(accepted=0, rejected=[{"row": 2, "reason": "Unknown category 'X'"}])


@router.get("", response_model=Page[s.ComplaintRow], dependencies=[Depends(fx.stub)])
def list_complaints(status: str | None = None, priority: str | None = None, category: str | None = None,
                    sla_state: str | None = None, ward_id: str | None = None, escalated: bool | None = None,
                    source: str | None = None, q: str | None = None, page: int = 1, page_size: int = 10,
                    format: str | None = None):
    return Page(items=[fx.row(), fx.row("SR-2026-000124")], total=2, page=page, page_size=page_size)


@router.get("/{sr_id}", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def get_complaint(sr_id: str):
    return fx.detail()


@router.get("/{sr_id}/analysis", response_model=s.AnalysisView, dependencies=[Depends(fx.stub)])
def analysis(sr_id: str):
    return s.AnalysisView(run=fx.run_detail(), brief=fx.brief(), duplicate_suggestions=[
        s.DuplicateSuggestion(sr_id="SR-2026-000119", confidence=0.72, distance_m=18, status="SUBMITTED")])


@router.post("/{sr_id}/confirm", response_model=Ok, dependencies=[Depends(fx.stub)])
def confirm(sr_id: str, body: s.ConfirmIn):
    return Ok()


@router.post("/{sr_id}/reopen", response_model=Ok, dependencies=[Depends(fx.stub)])
def reopen(sr_id: str, body: s.ReopenIn):
    return Ok()


@router.post("/{sr_id}/accept", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def accept(sr_id: str, body: s.AcceptIn):
    return fx.detail()


@router.post("/{sr_id}/override", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def override(sr_id: str, body: s.OverrideIn):
    return fx.detail()


@router.post("/{sr_id}/merge", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def merge(sr_id: str, body: s.MergeIn):
    return fx.detail()


@router.post("/{sr_id}/unmerge", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def unmerge(sr_id: str, body: s.ReasonIn):
    return fx.detail()


@router.post("/{sr_id}/reject", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def reject(sr_id: str, body: s.RejectIn):
    return fx.detail()


@router.post("/{sr_id}/hold", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def hold(sr_id: str, body: s.HoldIn):
    return fx.detail()


@router.post("/{sr_id}/resume", response_model=s.ComplaintDetail, dependencies=[Depends(fx.stub)])
def resume(sr_id: str):
    return fx.detail()


@router.post("/{sr_id}/work-orders", response_model=s.WorkOrderDetail, status_code=201,
             dependencies=[Depends(fx.stub)])
def create_work_order(sr_id: str, body: s.WorkOrderIn):
    return fx.wo_detail()
