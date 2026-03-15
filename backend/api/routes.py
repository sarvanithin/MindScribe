import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.api.schemas import (
    StartScreeningRequest, ScreeningResponseRequest, GenerateNoteRequest,
)
from backend.screening.engine import (
    start_session, submit_response, get_session_result,
    get_patient_history, record_session_history,
)
from backend.notes.generator import generate_note
from backend.clinical.risk_flags import RISK_RESPONSE

router = APIRouter()

_clinical_dir = Path(__file__).parent.parent / "clinical"
_data_dir = Path(__file__).parent.parent / "data" / "demo_transcripts"

with open(_clinical_dir / "icd10_codes.json") as f:
    _ICD10_CODES = json.load(f)

# ---------------------------------------------------------------------------
# Screening endpoints
# ---------------------------------------------------------------------------
@router.post("/screening/start")
async def screening_start(req: StartScreeningRequest):
    if req.assessment_type not in ("PHQ9", "GAD7"):
        raise HTTPException(400, "assessment_type must be 'PHQ9' or 'GAD7'")
    result = await start_session(req.patient_id, req.assessment_type)
    return result


@router.post("/screening/respond")
async def screening_respond(req: ScreeningResponseRequest):
    try:
        result = await submit_response(req.session_id, req.response)
        # If complete, record to patient history
        if result.get("status") == "complete":
            # Extract patient_id from session
            from backend.screening.engine import _sessions
            session = _sessions.get(req.session_id)
            if session:
                record_session_history(session.patient_id, req.session_id)
            # Attach crisis resources if any risk flags
            if result["result"]["risk_flags"]:
                result["crisis_resources"] = RISK_RESPONSE
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/screening/result/{session_id}")
async def screening_result(session_id: str):
    try:
        return get_session_result(session_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/screening/history/{patient_id}")
async def screening_history(patient_id: str):
    return {"patient_id": patient_id, "history": get_patient_history(patient_id)}


# ---------------------------------------------------------------------------
# Note generator endpoints
# ---------------------------------------------------------------------------
@router.post("/notes/generate")
async def notes_generate(req: GenerateNoteRequest):
    if req.format not in ("DAP", "SOAP", "BIRP"):
        raise HTTPException(400, "format must be 'DAP', 'SOAP', or 'BIRP'")
    if not req.transcript.strip():
        raise HTTPException(400, "transcript cannot be empty")

    note = await generate_note(
        transcript=req.transcript,
        patient_context=req.patient_context.model_dump(),
        format=req.format,
        session_date=req.session_date,
        session_duration=req.session_duration,
        modality=req.modality,
    )
    return {"note": note.model_dump()}


# ---------------------------------------------------------------------------
# Clinical reference endpoints
# ---------------------------------------------------------------------------
@router.get("/clinical/icd10")
async def clinical_icd10(query: str = ""):
    if not query:
        return _ICD10_CODES
    q = query.lower()
    return [c for c in _ICD10_CODES if q in c["description"].lower() or q in c["code"].lower()]


# ---------------------------------------------------------------------------
# Demo transcripts
# ---------------------------------------------------------------------------
@router.get("/demo/transcripts")
async def demo_transcripts():
    transcripts = []
    for path in sorted(_data_dir.glob("*.json")):
        with open(path) as f:
            transcripts.append(json.load(f))
    return transcripts
