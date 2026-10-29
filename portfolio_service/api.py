"""Protected FastAPI interface for the portfolio AI service."""
import hmac
import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from core import PROJECT_NAME, analyze

app = FastAPI(
    title=PROJECT_NAME + " API",
    version="1.0.0",
    description="An environment-configured AI service for portfolio demonstrations."
)


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)


@app.get("/health")
def health():
    return {"status": "ok", "project": PROJECT_NAME}


@app.post("/v1/analyze")
def analyze_endpoint(
    request: AnalyzeRequest,
    x_service_key: str = Header(default="", alias="X-Service-Key")
):
    expected = os.getenv("PORTFOLIO_SERVICE_KEY", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Service authentication is not configured."
        )
    if not hmac.compare_digest(x_service_key, expected):
        raise HTTPException(status_code=401, detail="Invalid service key.")

    try:
        return analyze(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
