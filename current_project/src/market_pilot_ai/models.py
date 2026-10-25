from pydantic import BaseModel, Field


class MarketData(BaseModel):
    symbol: str
    price: float
    change_percent: float
    volume: int


class MarketResearchReport(BaseModel):
    symbol: str = Field(
        description="Stock symbol being analyzed"
    )

    summary: str = Field(
        description="Short market summary"
    )

    technical_view: str = Field(
        description="Technical analysis view"
    )

    fundamental_view: str = Field(
        description="Fundamental analysis view"
    )

    risk_level: str = Field(
        description="Low, Medium, or High"
    )

    score: float = Field(
        ge=0,
        le=100,
        description="Overall research score from 0 to 100"
    )

    recommendation: str = Field(
        description="Research conclusion based only on supplied information"
    )

    key_risks: list[str] = Field(
        default_factory=list,
        description="Important risks identified in the analysis"
    )