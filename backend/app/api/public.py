from fastapi import APIRouter, Depends

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.schemas import ERROR_RESPONSES

router = APIRouter(tags=["public"], responses=ERROR_RESPONSES)


@router.get("/public/stats", response_model=s.PublicStats, dependencies=[Depends(fx.stub)])
def stats():
    return s.PublicStats(total=245, resolved=180, within_sla_pct=81.5, avg_resolution_days=3.2, unique_issues=198)


@router.get("/public/ticker", response_model=list[s.TickerItem], dependencies=[Depends(fx.stub)])
def ticker():
    return [s.TickerItem(id="INC-2026-0001", text_en="Avoid Kengeri underpass; crews deployed.",
                         text_kn=None, published_at=fx.NOW)]


@router.get("/public/wards", response_model=list[s.WardDirectoryEntry], dependencies=[Depends(fx.stub)])
def wards():
    return [s.WardDirectoryEntry(id="W12", name="Kengeri", zone="Kengeri Zone", officer_name="Example Officer",
                                 officer_designation="Assistant Engineer", office_phone="080-0000000")]


@router.get("/public/search", response_model=s.SearchResult, dependencies=[Depends(fx.stub)])
def search(q: str):
    return s.SearchResult(grievances=[], pages=[s.SearchHit(title="Lodge Grievance", path="/lodge")], wards=[])


@router.post("/public/visit", response_model=s.VisitCount, dependencies=[Depends(fx.stub)])
def visit(body: s.VisitIn):
    return s.VisitCount(count=1)


@router.get("/public/visits", response_model=s.VisitCount, dependencies=[Depends(fx.stub)])
def visits():
    return s.VisitCount(count=1)


@router.get("/meta/categories", response_model=list[s.CategoryOut], dependencies=[Depends(fx.stub)])
def categories():
    return [s.CategoryOut(id="POTHOLE", name_en="Pothole", name_kn="ರಸ್ತೆ ಗುಂಡಿ", department_id="ROADS")]


@router.get("/meta/departments", response_model=list[s.DepartmentOut], dependencies=[Depends(fx.stub)])
def departments():
    return [s.DepartmentOut(id="ROADS", name="Roads & Infrastructure")]


@router.get("/meta/wards", response_model=list[s.WardOut], dependencies=[Depends(fx.stub)])
def meta_wards(geo: int = 0):
    return [s.WardOut(id="W12", name="Kengeri", zone="Kengeri Zone")]


@router.get("/meta/crews", response_model=list[s.CrewOut], dependencies=[Depends(fx.stub)])
def crews(ward_id: str | None = None):
    return [s.CrewOut(id="W12-A", name="Ward 12 Road Crew A", ward_id="W12", skills=["road"], capacity=4,
                      open_work_orders=2)]
