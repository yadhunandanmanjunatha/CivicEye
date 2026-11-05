from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors import ApiError
from app.main import create_app


def _client() -> TestClient:
    app = create_app()
    r = APIRouter()

    @r.get("/boom")
    def boom():
        raise ApiError("INVALID_TRANSITION", "Cannot move from CLOSED to ASSIGNED", {"from": "CLOSED"})

    app.include_router(r, prefix="/api/v1/_t")
    return TestClient(app)


def test_health():
    assert _client().get("/api/v1/health").json() == {"status": "ok"}


def test_api_error_shape():
    res = _client().get("/api/v1/_t/boom")
    assert res.status_code == 409
    assert res.json() == {"error": {"code": "INVALID_TRANSITION",
                                    "message": "Cannot move from CLOSED to ASSIGNED",
                                    "details": {"from": "CLOSED"}}}


def test_not_found_shape():
    res = _client().get("/api/v1/nope")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"
