from pydantic import BaseModel
from typing import Any


# ---------------------------------------------------------------------------
# Screening
# ---------------------------------------------------------------------------
class StartScreeningRequest(BaseModel):
    patient_id: str
    assessment_type: str  # "PHQ9" | "GAD7"


class ScreeningResponseRequest(BaseModel):
    session_id: str
    response: str


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
class PatientContext(BaseModel):
    patient_id: str = "demo-patient"
    primary_diagnosis: str = ""
    session_num: int | str = "Unknown"
    prev_phq9: int | str = "Not available"
    prev_gad7: int | str = "Not available"
    goals: list[str] = []


class GenerateNoteRequest(BaseModel):
    transcript: str
    patient_context: PatientContext = PatientContext()
    format: str = "DAP"           # "DAP" | "SOAP" | "BIRP"
    session_date: str | None = None
    session_duration: int = 53
    modality: str = "individual"
