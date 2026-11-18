from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Language = Literal["en", "hi", "kn"]
Verdict = Literal["SCAM", "SUSPICIOUS", "SAFE"]


class CheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=10000)
    language: Language = "en"

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message text must not be empty.")
        return value


class RuleExplanation(BaseModel):
    en: str
    hi: str
    kn: str


class MatchedReason(BaseModel):
    code: str
    risk_weight: int
    explanations: RuleExplanation


class CheckResponse(BaseModel):
    verdict: Verdict
    score: int = Field(ge=0, le=100)
    reasons: list[MatchedReason]
    extracted_links: list[str]
    explanation: str
    language: Language
