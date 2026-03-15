"""
Scorer: maps free-text patient responses to PHQ/GAD 0–3 scale scores.
Uses Gemini with strict JSON output + robust fallback parsing.
"""
import json
import re
from backend.config import DEMO_MODE
from backend.notes.prompts import SCORER_SYSTEM, SCORER_PROMPT
from backend.clinical.risk_flags import check_risk_flags
from backend.llm import chat_completion


# ---------------------------------------------------------------------------
# JSON extraction — Gemini sometimes wraps JSON in markdown fences
# ---------------------------------------------------------------------------
def _extract_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from Gemini's response text.
    Handles: bare JSON, ```json ... ``` fences, prose + JSON mixed output.
    """
    # 1. Try direct parse first
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Find first {...} block with a regex
    match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 4. Give up — return a safe default
    return {}


def _heuristic_score(response_text: str) -> int:
    """
    Simple heuristic scorer for demo mode / fallback.
    Looks for frequency keywords.
    """
    text = response_text.lower()
    if any(w in text for w in ["never", "not at all", "no", "nope", "not really"]):
        return 0
    if any(w in text for w in ["sometimes", "a bit", "occasionally", "somewhat", "a little", "a few days"]):
        return 1
    if any(w in text for w in ["often", "frequently", "most", "more than half", "usually", "a lot"]):
        return 2
    if any(w in text for w in ["always", "every day", "constantly", "all the time", "nearly every"]):
        return 3
    # Default to 1 if truly ambiguous
    return 1


async def score_response(
    assessment_type: str,
    question_num: int,
    domain: str,
    standard_question: str,
    conversational_prompt: str,
    patient_response: str,
) -> dict:
    """
    Returns: {
        score: int (0–3),
        confidence: float,
        reasoning: str,
        follow_up_needed: bool,
        risk_flag: str | None
    }
    """
    # Always run keyword risk check regardless of LLM output
    keyword_flags = check_risk_flags(patient_response)

    if DEMO_MODE:
        score = _heuristic_score(patient_response)
        risk_flag = keyword_flags[0] if keyword_flags else None
        # Q9 special handling in demo
        if domain == "suicidal_ideation" and score > 0:
            risk_flag = "suicidal_ideation"
        return {
            "score": score,
            "confidence": 0.70,
            "reasoning": "Demo mode: heuristic keyword scoring",
            "follow_up_needed": False,
            "risk_flag": risk_flag,
        }

    try:
        prompt = SCORER_PROMPT.format(
            assessment_type=assessment_type,
            question_num=question_num,
            domain=domain,
            standard_question=standard_question,
            conversational_prompt=conversational_prompt,
            patient_response=patient_response,
        )
        raw = await chat_completion(
            system=SCORER_SYSTEM,
            user=prompt,
            temperature=0.1,
            json_mode=True,
        )
        parsed = _extract_json(raw)

        score = int(parsed.get("score", _heuristic_score(patient_response)))
        score = max(0, min(3, score))  # clamp to 0–3

        risk_flag = parsed.get("risk_flag") or (keyword_flags[0] if keyword_flags else None)

        # Always override: any Q9 positive → flag
        if domain == "suicidal_ideation" and score > 0:
            risk_flag = "suicidal_ideation"

        return {
            "score": score,
            "confidence": float(parsed.get("confidence", 0.80)),
            "reasoning": parsed.get("reasoning", ""),
            "follow_up_needed": bool(parsed.get("follow_up_needed", False)),
            "risk_flag": risk_flag,
        }
    except Exception as e:
        print(f"[Scorer] Groq error: {e} — using heuristic fallback")
        score = _heuristic_score(patient_response)
        risk_flag = keyword_flags[0] if keyword_flags else None
        if domain == "suicidal_ideation" and score > 0:
            risk_flag = "suicidal_ideation"
        return {
            "score": score,
            "confidence": 0.50,
            "reasoning": f"Heuristic fallback (LLM error: {str(e)[:80]})",
            "follow_up_needed": False,
            "risk_flag": risk_flag,
        }
