"""
Screening engine: orchestrates the full multi-turn screening conversation.
Maintains session state in-memory (intentional — no PHI persistence).
"""
import uuid
from datetime import datetime
from backend.models.screening import ScreeningSession, ScreeningResponse
from backend.screening.phq9 import PHQ9_QUESTIONS, get_phq9_severity, PHQ9_MAX_SCORE
from backend.screening.gad7 import GAD7_QUESTIONS, get_gad7_severity, GAD7_MAX_SCORE
from backend.screening.adapter import get_conversational_question
from backend.screening.scorer import score_response
from backend.config import DEMO_MODE
from backend.notes.prompts import INTERPRETATION_PROMPT
from backend.llm import chat_completion

# In-memory session store: session_id -> ScreeningSession
# NOTE: state is lost on server restart — acceptable for demo, document clearly
_sessions: dict[str, ScreeningSession] = {}


def _get_questions(assessment_type: str) -> list[dict]:
    if assessment_type == "PHQ9":
        return PHQ9_QUESTIONS
    elif assessment_type == "GAD7":
        return GAD7_QUESTIONS
    raise ValueError(f"Unknown assessment type: {assessment_type}")


def _get_max_score(assessment_type: str) -> int:
    return PHQ9_MAX_SCORE if assessment_type == "PHQ9" else GAD7_MAX_SCORE


def _get_severity(assessment_type: str, score: int) -> str:
    if assessment_type == "PHQ9":
        return get_phq9_severity(score)
    return get_gad7_severity(score)


def _build_prior_context(session: ScreeningSession) -> str:
    if not session.responses:
        return ""
    lines = []
    for r in session.responses:
        severity_hint = ""
        if r.mapped_score == 3:
            severity_hint = " (nearly every day)"
        elif r.mapped_score == 2:
            severity_hint = " (more than half the days)"
        elif r.mapped_score == 1:
            severity_hint = " (several days)"
        else:
            severity_hint = " (not at all)"
        lines.append(f"Q{r.question_number} [{r.domain}]: patient said '{r.patient_response[:80]}' → score {r.mapped_score}{severity_hint}")
    return "\n".join(lines)


async def _generate_interpretation(session: ScreeningSession) -> str:
    if DEMO_MODE:
        score = session.total_score or 0
        severity = session.severity or "unknown"
        assessment = session.assessment_type
        return (
            f"Patient completed {assessment} with a total score of {score}/{_get_max_score(assessment)}, "
            f"indicating {severity} symptom severity. "
            f"Clinician review recommended to validate findings and discuss treatment options. "
            f"{'⚠ Safety flags detected — immediate clinical follow-up required.' if session.risk_flags else 'No safety flags detected during this screening.'}"
        )
    try:
        domain_lines = "\n".join(
            f"  {r.domain}: {r.mapped_score}/3" for r in session.responses
        )
        prompt = INTERPRETATION_PROMPT.format(
            assessment_type=session.assessment_type,
            total_score=session.total_score,
            max_score=_get_max_score(session.assessment_type),
            severity=session.severity,
            domain_breakdown=domain_lines,
            risk_flags=", ".join(session.risk_flags) if session.risk_flags else "None",
        )
        return await chat_completion(system="You are a clinical documentation assistant.", user=prompt, temperature=0.3)
    except Exception as e:
        print(f"[Engine] Interpretation error: {e}")
        return f"Screening complete. Score: {session.total_score}. Severity: {session.severity}."


async def start_session(patient_id: str, assessment_type: str) -> dict:
    """Create a new screening session and return the first question."""
    questions = _get_questions(assessment_type)
    session_id = str(uuid.uuid4())
    session = ScreeningSession(
        id=session_id,
        patient_id=patient_id,
        assessment_type=assessment_type,
        started_at=datetime.utcnow(),
    )
    _sessions[session_id] = session

    first_q = questions[0]
    conversational = await get_conversational_question(
        assessment_type=assessment_type,
        question_num=1,
        total_questions=len(questions),
        standard_question=first_q["text"],
        domain=first_q["domain"],
        prior_context="",
    )

    return {
        "session_id": session_id,
        "question_number": 1,
        "total_questions": len(questions),
        "question_text": conversational,
        "domain": first_q["domain"],
        "assessment_type": assessment_type,
    }


async def submit_response(session_id: str, patient_response: str) -> dict:
    """
    Accept a patient response, score it, advance to next question or finish.
    Returns either the next question or the final results.
    """
    session = _sessions.get(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    questions = _get_questions(session.assessment_type)
    answered_count = len(session.responses)

    if answered_count >= len(questions):
        raise ValueError("All questions already answered.")

    current_q = questions[answered_count]
    prior_conv_prompt = ""
    if answered_count > 0:
        prior_conv_prompt = session.responses[-1].conversational_prompt

    # Get conversational prompt used for this question
    conv_prompt = await get_conversational_question(
        assessment_type=session.assessment_type,
        question_num=answered_count + 1,
        total_questions=len(questions),
        standard_question=current_q["text"],
        domain=current_q["domain"],
        prior_context=_build_prior_context(session),
    )

    # Score the response
    result = await score_response(
        assessment_type=session.assessment_type,
        question_num=answered_count + 1,
        domain=current_q["domain"],
        standard_question=current_q["text"],
        conversational_prompt=conv_prompt,
        patient_response=patient_response,
    )

    # Record the response
    response_record = ScreeningResponse(
        question_number=answered_count + 1,
        standard_question=current_q["text"],
        conversational_prompt=conv_prompt,
        patient_response=patient_response,
        mapped_score=result["score"],
        confidence=result["confidence"],
        notes=result.get("reasoning"),
        risk_flag=result.get("risk_flag"),
        domain=current_q["domain"],
    )
    session.responses.append(response_record)

    # Accumulate risk flags
    if result.get("risk_flag"):
        flag = f"{result['risk_flag']}_q{answered_count + 1}"
        if flag not in session.risk_flags:
            session.risk_flags.append(flag)

    next_q_num = answered_count + 2  # 1-indexed next question
    is_complete = next_q_num > len(questions)

    if is_complete:
        # Finalize session
        total = sum(r.mapped_score for r in session.responses)
        session.total_score = total
        session.severity = _get_severity(session.assessment_type, total)
        session.completed_at = datetime.utcnow()
        session.clinical_interpretation = await _generate_interpretation(session)
        _sessions[session_id] = session

        return {
            "status": "complete",
            "question_number": answered_count + 1,
            "mapped_score": result["score"],
            "risk_flag": result.get("risk_flag"),
            "result": {
                "total_score": total,
                "max_score": _get_max_score(session.assessment_type),
                "severity": session.severity,
                "risk_flags": session.risk_flags,
                "clinical_interpretation": session.clinical_interpretation,
                "responses": [r.model_dump() for r in session.responses],
            },
        }
    else:
        # Return next question
        next_q = questions[next_q_num - 1]
        next_conv = await get_conversational_question(
            assessment_type=session.assessment_type,
            question_num=next_q_num,
            total_questions=len(questions),
            standard_question=next_q["text"],
            domain=next_q["domain"],
            prior_context=_build_prior_context(session),
        )
        return {
            "status": "in_progress",
            "question_number": next_q_num,
            "total_questions": len(questions),
            "question_text": next_conv,
            "domain": next_q["domain"],
            "mapped_score": result["score"],
            "risk_flag": result.get("risk_flag"),
            "running_total": sum(r.mapped_score for r in session.responses),
        }


def get_session_result(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    if not session.completed_at:
        raise ValueError("Session not yet completed.")
    return {
        "total_score": session.total_score,
        "max_score": _get_max_score(session.assessment_type),
        "severity": session.severity,
        "risk_flags": session.risk_flags,
        "clinical_interpretation": session.clinical_interpretation,
        "responses": [r.model_dump() for r in session.responses],
        "assessment_type": session.assessment_type,
        "started_at": session.started_at.isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }


# Per-patient history (accumulated in-memory across sessions)
_patient_history: dict[str, list[dict]] = {}


def record_session_history(patient_id: str, session_id: str):
    """After a session completes, save a summary to patient history."""
    session = _sessions.get(session_id)
    if not session or not session.completed_at:
        return
    entry = {
        "session_id": session_id,
        "assessment_type": session.assessment_type,
        "total_score": session.total_score,
        "max_score": _get_max_score(session.assessment_type),
        "severity": session.severity,
        "completed_at": session.completed_at.isoformat(),
        "risk_flags": session.risk_flags,
    }
    _patient_history.setdefault(patient_id, []).append(entry)


def get_patient_history(patient_id: str) -> list[dict]:
    return _patient_history.get(patient_id, [])
