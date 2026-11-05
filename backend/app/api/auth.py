from fastapi import APIRouter, Depends, Response

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.schemas import ERROR_RESPONSES, Page

router = APIRouter(tags=["auth"], responses=ERROR_RESPONSES)
staff = APIRouter(prefix="/staff", tags=["staff"], responses=ERROR_RESPONSES)


@router.post("/auth/register", response_model=s.UserOut, dependencies=[Depends(fx.stub)])
def register(body: s.RegisterIn):
    return fx.user("CITIZEN")


@router.post("/auth/login", response_model=s.UserOut, dependencies=[Depends(fx.stub)])
def login(body: s.LoginIn):
    return fx.user()


@router.post("/auth/logout", status_code=204, dependencies=[Depends(fx.stub)])
def logout():
    return Response(status_code=204)


@router.get("/auth/me", response_model=s.UserOut, dependencies=[Depends(fx.stub)])
def me():
    return fx.user()


@router.get("/captcha", response_model=s.CaptchaOut, dependencies=[Depends(fx.stub)])
def captcha():
    return s.CaptchaOut(captcha_id=fx.UID, question="What is 4 + 7?")


@staff.get("", response_model=Page[s.StaffOut], dependencies=[Depends(fx.stub)])
def list_staff(role: str | None = None, ward_id: str | None = None, q: str | None = None,
               page: int = 1, page_size: int = 10, format: str | None = None):
    u = s.StaffOut(**fx.user().model_dump(), is_active=True, created_at=fx.NOW)
    return Page(items=[u], total=1, page=page, page_size=page_size)


@staff.post("", response_model=s.StaffOut, status_code=201, dependencies=[Depends(fx.stub)])
def create_staff(body: s.StaffIn):
    return s.StaffOut(**fx.user(body.role).model_dump(), is_active=True, created_at=fx.NOW)


@staff.patch("/{user_id}", response_model=s.StaffOut, dependencies=[Depends(fx.stub)])
def update_staff(user_id: str, body: s.StaffPatch):
    return s.StaffOut(**fx.user().model_dump(), is_active=True, created_at=fx.NOW)
