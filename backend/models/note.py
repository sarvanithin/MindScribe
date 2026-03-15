from pydantic import BaseModel


class DiagnosisCode(BaseModel):
    code: str           # "F32.1"
    description: str    # "Major depressive disorder, single episode, moderate"
    primary: bool       # is this the primary diagnosis?


class SessionNote(BaseModel):
    id: str
    patient_id: str
    session_date: str
    session_duration: int             # minutes
    format: str                       # "DAP" | "SOAP" | "BIRP"
    modality: str                     # "individual" | "group" | "family" | "couples"

    # Core sections (vary by format)
    sections: dict[str, str]          # {"data": "...", "assessment": "...", "plan": "..."}

    # Clinical coding
    diagnosis_codes: list[DiagnosisCode] = []
    cpt_code: str = ""                # e.g. "90837"

    # Metadata
    treatment_goals: list[str] = []
    interventions_used: list[str] = []
    risk_assessment: str = ""         # "no current SI/HI" or flagged concerns
    next_session: str = ""

    full_text: str                    # complete formatted note
