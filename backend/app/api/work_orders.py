from typing import Literal

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.schemas import ERROR_RESPONSES, Page

router = APIRouter(tags=["work orders"], responses=ERROR_RESPONSES)


@router.get("/work-orders/mine", response_model=Page[s.WorkOrderRow], dependencies=[Depends(fx.stub)])
def mine(status: str | None = None, page: int = 1, page_size: int = 10):
    return Page(items=[fx.wo_row()], total=1, page=page, page_size=page_size)


@router.get("/work-orders/{wo_id}", response_model=s.WorkOrderDetail, dependencies=[Depends(fx.stub)])
def get_wo(wo_id: str):
    return fx.wo_detail()


@router.post("/work-orders/{wo_id}/start", response_model=s.WorkOrderDetail, dependencies=[Depends(fx.stub)])
def start(wo_id: str):
    return fx.wo_detail()


@router.post("/work-orders/{wo_id}/photos", response_model=s.Attachment, status_code=201,
             dependencies=[Depends(fx.stub)])
def upload_photo(wo_id: str, kind: Literal["BEFORE", "AFTER"] = Form(...), photo: UploadFile = File(...)):
    return fx.attachment(kind)


@router.post("/work-orders/{wo_id}/complete", response_model=s.WorkOrderDetail, dependencies=[Depends(fx.stub)])
def complete(wo_id: str):
    return fx.wo_detail()


@router.get("/verification-queue", response_model=Page[s.VerificationItem], dependencies=[Depends(fx.stub)])
def verification_queue(page: int = 1, page_size: int = 10, format: str | None = None):
    item = s.VerificationItem(wo_id="WO-2026-000041", sr_id="SR-2026-000123", crew_id="W12-A",
                              category="POTHOLE", completed_at=fx.NOW, before=fx.attachment("BEFORE"),
                              after=fx.attachment("AFTER"), audit=fx.audit(), audit_pending=False)
    return Page(items=[item], total=1, page=page, page_size=page_size)


@router.post("/work-orders/{wo_id}/approve", response_model=s.WorkOrderDetail, dependencies=[Depends(fx.stub)])
def approve(wo_id: str):
    return fx.wo_detail()


@router.post("/work-orders/{wo_id}/reject", response_model=s.WorkOrderDetail, dependencies=[Depends(fx.stub)])
def reject(wo_id: str, body: s.ReasonIn):
    return fx.wo_detail()
