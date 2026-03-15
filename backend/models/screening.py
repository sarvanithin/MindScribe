from datetime import datetime
from pydantic import BaseModel


class ScreeningResponse(BaseModel):
    question_number: int
    domain: str                   # e.g. "anhedonia", "mood", "nervousness"
    standard_question: str        # original PHQ-9/GAD-7 text
    conversational_prompt: str    # what the AI actually said
    patient_response: str         # what the patient said
    mapped_score: int             # 0–3 (not at all / several days / more than half / nearly every day)
    confidence: float             # 0.0–1.0 how confident the mapping is
    notes: str | None = None      # any context from the response
    risk_flag: str | None = None  # "suicidal_ideation" | "self_harm" | "homicidal" | None


class ScreeningSession(BaseModel):
    id: str
    patient_id: str
    assessment_type: str                   # "PHQ9" | "GAD7"
    started_at: datetime
    completed_at: datetime | None = None
    responses: list[ScreeningResponse] = []
    total_score: int | None = None
    severity: str | None = None            # "minimal" | "mild" | "moderate" | "moderately_severe" | "severe"
    risk_flags: list[str] = []             # e.g. ["suicidal_ideation_q9"]
    clinical_interpretation: str | None = None  # AI-generated summary
