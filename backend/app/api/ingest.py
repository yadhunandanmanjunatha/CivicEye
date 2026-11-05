from fastapi import APIRouter, Depends, File, Header, UploadFile

from app.api import fixtures as fx
from app.api import schemas as s
from app.core.schemas import ERROR_RESPONSES

router = APIRouter(prefix="/ingest", tags=["ingestion"], responses=ERROR_RESPONSES)


@router.post("/detections", response_model=s.IngestResult, dependencies=[Depends(fx.stub)])
def detections(body: s.DetectionBatch, x_api_key: str = Header(...),
               idempotency_key: str | None = Header(None)):
    """Batch of up to 1,000 hazard detections. Record fields: see `DetectionIn` / CONTRACTS §4."""
    return s.IngestResult(accepted=len(body.records), rejected=0, duplicates=0, rejections=[])


@router.post("/detections/csv", response_model=s.IngestResult, dependencies=[Depends(fx.stub)])
def detections_csv(file: UploadFile = File(...), x_api_key: str = Header(...)):
    return s.IngestResult(accepted=0, rejected=0, duplicates=0, rejections=[])


@router.post("/weather-alerts", response_model=s.IngestResult, dependencies=[Depends(fx.stub)])
def weather_alerts(body: s.WeatherAlertIn, x_api_key: str = Header(...)):
    return s.IngestResult(accepted=1, rejected=0, duplicates=0, rejections=[])
