from fastapi import APIRouter, Depends

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.schemas import ERROR_RESPONSES, Page

router = APIRouter(tags=["follow-up"], responses=ERROR_RESPONSES)


def _proposal() -> s.ProposalOut:
    return s.ProposalOut(id=1, wo_id="WO-2026-000052", sr_id="SR-2026-000130", from_crew_id="W13-A",
                         to_crew_id="W12-B", reason="Crew W13-A has 9 open jobs (capacity 4); W12-B is free 1.2 km away.",
                         evidence={"from_load": 9, "from_capacity": 4, "distance_km": 1.2}, status="PENDING",
                         created_at=fx.NOW)


@router.get("/proposals", response_model=list[s.ProposalOut], dependencies=[Depends(fx.stub)])
def proposals(status: str = "PENDING"):
    return [_proposal()]


@router.post("/proposals/{proposal_id}/approve", response_model=s.ProposalOut, dependencies=[Depends(fx.stub)])
def approve(proposal_id: int):
    return _proposal()


@router.post("/proposals/{proposal_id}/reject", response_model=s.ProposalOut, dependencies=[Depends(fx.stub)])
def reject(proposal_id: int, body: s.ReasonIn):
    return _proposal()


@router.get("/referrals", response_model=Page[s.ReferralOut], dependencies=[Depends(fx.stub)])
def referrals(agency: str | None = None, status: str | None = None, page: int = 1, page_size: int = 10,
              format: str | None = None):
    return Page(items=[fx.referral()], total=1, page=page, page_size=page_size)


def _agency_ref() -> s.AgencyReferral:
    return s.AgencyReferral(**fx.referral().model_dump(), category="STREETLIGHT",
                            description="Streetlight not working for a week", location=s.LatLon(lat=12.9, lon=77.48),
                            address="Kengeri bus stand", asset_id="STREETLIGHT-W12-00871")


@router.get("/agency/referrals", response_model=Page[s.AgencyReferral], dependencies=[Depends(fx.stub)])
def agency_referrals(status: str | None = None, page: int = 1, page_size: int = 10):
    return Page(items=[_agency_ref()], total=1, page=page, page_size=page_size)


@router.post("/agency/referrals/{referral_id}/reply", response_model=s.AgencyReferral,
             dependencies=[Depends(fx.stub)])
def agency_reply(referral_id: str, body: s.AgencyReplyIn):
    return _agency_ref()


@router.get("/escalations", response_model=Page[s.EscalationOut], dependencies=[Depends(fx.stub)])
def escalations(level: int | None = None, page: int = 1, page_size: int = 10, format: str | None = None):
    e = s.EscalationOut(id=1, sr_id="SR-2026-000124", level=2, trigger="AGENCY_NO_RESPONSE",
                        reason_summary="Waiting on BESCOM feeder repair; followed up twice, no response.",
                        authority_name="Zonal Officer", authority_designation="Assistant Executive Engineer",
                        created_at=fx.NOW, deadline=None)
    return Page(items=[e], total=1, page=page, page_size=page_size)


@router.get("/inventory", response_model=list[s.InventoryOut], dependencies=[Depends(fx.stub)])
def inventory():
    return [s.InventoryOut(item="cold_mix_asphalt", name="Cold-mix asphalt", unit="bag", qty=0,
                           out_of_stock_since=fx.NOW)]


@router.get("/material-requests", response_model=Page[s.MaterialRequestOut], dependencies=[Depends(fx.stub)])
def material_requests(page: int = 1, page_size: int = 10, format: str | None = None):
    m = s.MaterialRequestOut(id=1, item="cold_mix_asphalt", qty=20, sr_id="SR-2026-000130",
                             reason="Out of stock; needed for pothole job", status="OPEN",
                             raised_by="followup_escalation", created_at=fx.NOW)
    return Page(items=[m], total=1, page=page, page_size=page_size)
