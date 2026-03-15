from pydantic import BaseModel


class Patient(BaseModel):
    id: str
    display_name: str              # e.g. "Client A" — never real name
    age_range: str | None = None   # "25-35" — never exact DOB
    primary_diagnosis: str | None = None
    session_count: int = 0
    created_at: str = ""
