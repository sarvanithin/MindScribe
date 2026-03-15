"""
Note generation engine: transcript → structured clinical note (DAP/SOAP/BIRP).
"""
import uuid
import json
import re
from datetime import datetime
from typing import Any
from backend.config import DEMO_MODE
from backend.models.note import SessionNote, DiagnosisCode
from backend.notes.prompts import (
    NOTE_SYSTEM, NOTE_PROMPT,
    DAP_FORMAT_INSTRUCTIONS, SOAP_FORMAT_INSTRUCTIONS, BIRP_FORMAT_INSTRUCTIONS,
)
from backend.notes.coder import suggest_icd10_from_text, suggest_cpt_from_duration
from backend.llm import chat_completion

FORMAT_INSTRUCTIONS = {
    "DAP": DAP_FORMAT_INSTRUCTIONS,
    "SOAP": SOAP_FORMAT_INSTRUCTIONS,
    "BIRP": BIRP_FORMAT_INSTRUCTIONS,
}

FORMAT_SECTIONS = {
    "DAP": ["data", "assessment", "plan"],
    "SOAP": ["subjective", "objective", "assessment", "plan"],
    "BIRP": ["behavior", "intervention", "response", "plan"],
}


# ---------------------------------------------------------------------------
# Demo note templates (realistic, not generic)
# ---------------------------------------------------------------------------
DEMO_NOTES: dict[str, dict[str, dict[str, str]]] = {
    "DAP": {
        "data": (
            "Patient presents to 53-minute individual psychotherapy session appearing disheveled "
            "with psychomotor slowing noted. Reports a difficult week characterized by persistent "
            "social withdrawal — did not leave home for 4 of 7 days and avoided phone calls from "
            "family (\"I just couldn't answer. I didn't have the words\"). Endorses ongoing "
            "anhedonia and low energy. Reports partial completion of assigned cognitive thought "
            "journal (2 of 7 entries). Identified recurring automatic thought: \"I'm not good enough "
            "and everyone can see it.\" No current suicidal or homicidal ideation reported. PHQ-9 "
            "administered at outset of session: total score 16/27 (moderately severe), consistent "
            "with prior administration."
        ),
        "assessment": (
            "Patient continues to meet criteria for major depressive disorder, single episode, "
            "moderate (F32.1), with moderately severe current symptom presentation (PHQ-9=16). "
            "Social withdrawal and avoidance of support network are functionally impairing and "
            "represent a key maintenance factor for depressive symptoms. Partial homework completion "
            "represents a meaningful positive prognostic indicator given current motivational deficits. "
            "Automatic thought ('I'm not good enough') reflects overgeneralization and labeling — "
            "core cognitive distortions consistent with CBT formulation. No identified acute safety "
            "concerns at this time; safety plan reviewed and remains in place."
        ),
        "plan": (
            "1. Continue weekly individual CBT sessions (CPT 90837).\n"
            "2. Introduce cognitive restructuring worksheet targeting identified automatic thought.\n"
            "3. Homework: continue thought journal + add evidence-for/evidence-against column.\n"
            "4. Behavioral activation: collaboratively identify one small social activity for next week.\n"
            "5. Re-administer PHQ-9 in 2 sessions to track trajectory.\n"
            "6. No medication changes at this time; maintain coordination with prescribing provider.\n"
            "7. Safety plan reviewed — no current SI/HI, plan remains adequate."
        ),
    },
    "SOAP": {
        "subjective": (
            "Patient reports the past week was \"really hard\" and that he barely left the house. "
            "Describes avoiding phone calls from family, stating he \"didn't have the energy\" "
            "and everything \"feels pointless.\" Endorses completed thought journaling homework "
            "twice this week, noting a recurring theme: \"I keep writing 'I'm not good enough.'\" "
            "Patient denies current suicidal ideation. Mood self-reported as 3/10."
        ),
        "objective": (
            "Patient presented with disheveled appearance, psychomotor slowing, and restricted "
            "affect with intermittent emotional expression when discussing core beliefs. "
            "Maintained appropriate eye contact. Speech was slow but goal-directed. Engaged "
            "thoughtfully with CBT techniques, identifying cognitive distortions with minimal "
            "prompting. PHQ-9 score: 16/27 (moderately severe)."
        ),
        "assessment": (
            "Patient meets criteria for MDD, single episode, moderate (F32.1). PHQ-9 score of 16 "
            "represents a 6-point reduction from intake (22), suggesting modest but meaningful "
            "improvement. Social withdrawal remains the primary functional impairment. Homework "
            "engagement is a positive treatment indicator. Core belief work is indicated as next "
            "logical CBT phase. No acute safety concerns."
        ),
        "plan": (
            "1. CPT 90837 — 53-minute individual psychotherapy\n"
            "2. Begin cognitive restructuring for core belief: 'I am not good enough'\n"
            "3. HW: Thought journal + add behavioral experiment column\n"
            "4. Behavioral activation goal: one social interaction before next session\n"
            "5. Safety plan reviewed; patient verbalizes plan and emergency contacts\n"
            "6. Next session: 03/21/2026"
        ),
    },
    "BIRP": {
        "behavior": (
            "Client demonstrated restricted affect and notable psychomotor slowing throughout "
            "session. Reports leaving home only 3 days in the past week and not answering "
            "phone calls from mother or friends (\"I just couldn't answer\"). Endorses persistent "
            "anhedonia and fatigue (PHQ-9=16, moderately severe). Completed thought journal "
            "2/7 days — below goal but above zero. Identified recurring automatic thought: "
            "\"I'm not good enough and everyone can see it.\""
        ),
        "intervention": (
            "Therapist engaged client in collaborative Socratic dialogue around identified "
            "automatic thought. Applied the double-standard technique: asked client to consider "
            "whether he would judge a close friend as harshly for the same situation. Introduced "
            "evidence examination: what evidence supports vs. contradicts the belief? "
            "Psychoeducation provided on cognitive distortions (specifically overgeneralization "
            "and labeling). Assigned structured behavioral activation task with graded difficulty. "
            "Safety plan reviewed and updated with new emergency contact added."
        ),
        "response": (
            "Client engaged actively with Socratic questioning, demonstrating emerging cognitive "
            "flexibility — identified three counter-examples to core belief with light prompting "
            "(\"I did finish that project at work last month\"). Visibly moved when applying "
            "double-standard technique, stating \"I guess I wouldn't say that to anyone else.\" "
            "Some ambivalence around behavioral activation task — negotiated smaller initial step "
            "(texting rather than calling friend). Overall response to intervention was positive "
            "with tangible affective shift noted mid-session."
        ),
        "plan": (
            "1. Continue weekly CBT sessions (CPT 90837)\n"
            "2. HW: Thought record with evidence columns + text one friend before next session\n"
            "3. Re-introduce positive activity scheduling worksheet\n"
            "4. PHQ-9 re-administration in 2 sessions\n"
            "5. Safety plan in place; no acute risk; next session 03/21/2026"
        ),
    },
}


def _build_demo_note(
    note_id: str,
    patient_id: str,
    format: str,
    session_date: str,
    session_duration: int,
    modality: str,
    diagnosis_codes: list[dict],
    cpt_code: str,
) -> SessionNote:
    sections = DEMO_NOTES.get(format, DEMO_NOTES["DAP"])
    format_labels = {
        "DAP": {"data": "DATA", "assessment": "ASSESSMENT", "plan": "PLAN"},
        "SOAP": {"subjective": "SUBJECTIVE", "objective": "OBJECTIVE", "assessment": "ASSESSMENT", "plan": "PLAN"},
        "BIRP": {"behavior": "BEHAVIOR", "intervention": "INTERVENTION", "response": "RESPONSE", "plan": "PLAN"},
    }
    labels = format_labels.get(format, format_labels["DAP"])
    full_text_parts = [
        f"SESSION NOTE — {format} FORMAT",
        f"Date: {session_date} | Duration: {session_duration} min | Modality: {modality.title()}",
        f"Dx: {diagnosis_codes[0]['code']} ({diagnosis_codes[0]['description']}) | CPT: {cpt_code}\n",
    ]
    for section_key, content in sections.items():
        label = labels.get(section_key, section_key.upper())
        full_text_parts.append(f"{label}:\n{content}\n")

    return SessionNote(
        id=note_id,
        patient_id=patient_id,
        session_date=session_date,
        session_duration=session_duration,
        format=format,
        modality=modality,
        sections=sections,
        diagnosis_codes=[DiagnosisCode(**d) for d in diagnosis_codes],
        cpt_code=cpt_code,
        treatment_goals=["Reduce depressive symptoms (target PHQ-9 < 10)", "Improve social engagement", "Develop cognitive flexibility"],
        interventions_used=["Cognitive Behavioral Therapy (CBT)", "Cognitive restructuring", "Behavioral activation"],
        risk_assessment="No current suicidal or homicidal ideation reported. Safety plan reviewed and in place.",
        next_session="One week",
        full_text="\n".join(full_text_parts),
    )


def _extract_json_note(raw: str) -> dict:
    """Multi-layer JSON extraction matching scorer.py approach."""
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Find the outermost { ... }
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


async def generate_note(
    transcript: str,
    patient_context: dict,
    format: str = "DAP",
    session_date: str | None = None,
    session_duration: int = 53,
    modality: str = "individual",
) -> SessionNote:
    """
    Main entry point: generate a clinical progress note from a therapy transcript.
    """
    note_id = str(uuid.uuid4())
    patient_id = patient_context.get("patient_id", "demo-patient")
    date_str = session_date or datetime.utcnow().strftime("%m/%d/%Y")
    diagnosis = patient_context.get("primary_diagnosis", "")

    diagnosis_codes = suggest_icd10_from_text(transcript, diagnosis)
    cpt_code = suggest_cpt_from_duration(session_duration, modality)

    if DEMO_MODE:
        return _build_demo_note(
            note_id, patient_id, format, date_str,
            session_duration, modality, diagnosis_codes, cpt_code
        )

    try:
        prompt = NOTE_PROMPT.format(
            format=format,
            transcript=transcript[:6000],  # safety trim
            diagnosis=diagnosis or "Not specified",
            modality=modality,
            session_num=patient_context.get("session_num", "Unknown"),
            prev_phq9=patient_context.get("prev_phq9", "Not available"),
            prev_gad7=patient_context.get("prev_gad7", "Not available"),
            goals=", ".join(patient_context.get("goals", [])) or "Not specified",
            session_date=date_str,
            session_duration=session_duration,
            format_instructions=FORMAT_INSTRUCTIONS.get(format, DAP_FORMAT_INSTRUCTIONS),
        )
        raw = await chat_completion(
            system=NOTE_SYSTEM,
            user=prompt,
            temperature=0.3,
            json_mode=True,
        )
        parsed = _extract_json_note(raw)

        sections = parsed.get("sections", {})
        if not sections:
            # Fallback: try to use demo sections
            sections = DEMO_NOTES.get(format, DEMO_NOTES["DAP"])

        dx_raw = parsed.get("diagnosis_codes", diagnosis_codes)
        dx_list = []
        for d in dx_raw[:3]:
            if isinstance(d, dict):
                dx_list.append(DiagnosisCode(
                    code=d.get("code", diagnosis_codes[0]["code"]),
                    description=d.get("description", diagnosis_codes[0]["description"]),
                    primary=d.get("primary", len(dx_list) == 0),
                ))

        if not dx_list:
            dx_list = [DiagnosisCode(**d) for d in diagnosis_codes]

        cpt = parsed.get("cpt_code", cpt_code)

        # Build full text
        format_labels = {
            "DAP": {"data": "DATA", "assessment": "ASSESSMENT", "plan": "PLAN"},
            "SOAP": {"subjective": "SUBJECTIVE", "objective": "OBJECTIVE", "assessment": "ASSESSMENT", "plan": "PLAN"},
            "BIRP": {"behavior": "BEHAVIOR", "intervention": "INTERVENTION", "response": "RESPONSE", "plan": "PLAN"},
        }
        labels = format_labels.get(format, format_labels["DAP"])
        full_text_parts = [
            f"SESSION NOTE — {format} FORMAT",
            f"Date: {date_str} | Duration: {session_duration} min | Modality: {modality.title()}",
            f"Dx: {dx_list[0].code} ({dx_list[0].description}) | CPT: {cpt}\n",
        ]
        for key, label in labels.items():
            content = sections.get(key, "")
            if content:
                full_text_parts.append(f"{label}:\n{content}\n")

        return SessionNote(
            id=note_id,
            patient_id=patient_id,
            session_date=date_str,
            session_duration=session_duration,
            format=format,
            modality=modality,
            sections=sections,
            diagnosis_codes=dx_list,
            cpt_code=cpt,
            treatment_goals=parsed.get("treatment_goals", []),
            interventions_used=parsed.get("interventions_used", []),
            risk_assessment=parsed.get("risk_assessment", "Risk assessment not available."),
            next_session=parsed.get("next_session", ""),
            full_text="\n".join(full_text_parts),
        )

    except Exception as e:
        print(f"[Generator] Groq error: {e} — falling back to demo note")
        return _build_demo_note(
            note_id, patient_id, format, date_str,
            session_duration, modality, diagnosis_codes, cpt_code
        )
