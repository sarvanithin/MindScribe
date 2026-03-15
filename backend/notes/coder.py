"""
ICD-10 + CPT code suggestion based on transcript keywords and LLM analysis.
"""
import json
import re
from pathlib import Path

_clinical_dir = Path(__file__).parent.parent / "clinical"

with open(_clinical_dir / "icd10_codes.json") as f:
    ICD10_CODES = json.load(f)

with open(_clinical_dir / "cpt_codes.json") as f:
    CPT_CODES = json.load(f)

# Keyword → ICD-10 code heuristics (supplements LLM)
KEYWORD_ICD10_MAP = {
    "depress": ["F32.1", "F33.1"],
    "hopeless": ["F32.1", "F33.1"],
    "suicid": ["F32.2"],
    "anxiet": ["F41.1"],
    "panic": ["F41.0"],
    "ptsd": ["F43.12"],
    "trauma": ["F43.10"],
    "adhd": ["F90.2"],
    "attention": ["F90.0"],
    "alcohol": ["F10.10"],
    "drinking": ["F10.10"],
    "borderline": ["F60.3"],
    "ocd": ["F42.2"],
    "obsess": ["F42.2"],
    "bipolar": ["F31.9"],
    "manic": ["F31.9"],
    "eating": ["F50.00"],
    "schizophrenia": ["F20.9"],
}

_icd10_lookup = {c["code"]: c["description"] for c in ICD10_CODES}


def suggest_icd10_from_text(transcript: str, primary_diagnosis: str | None = None) -> list[dict]:
    """
    Returns a list of suggested ICD-10 codes based on transcript keywords.
    primary_diagnosis takes precedence if provided.
    """
    found_codes: list[str] = []

    if primary_diagnosis:
        # Parse provided diagnosis code
        match = re.search(r"F\d{2}\.?\d*", primary_diagnosis.upper())
        if match and match.group() in _icd10_lookup:
            found_codes.append(match.group())

    text_lower = transcript.lower()
    for keyword, codes in KEYWORD_ICD10_MAP.items():
        if keyword in text_lower:
            for code in codes:
                if code not in found_codes:
                    found_codes.append(code)

    # Build result list (max 3 codes, first is primary)
    result = []
    for i, code in enumerate(found_codes[:3]):
        desc = _icd10_lookup.get(code, "Unknown")
        result.append({"code": code, "description": desc, "primary": i == 0})

    if not result:
        result.append({
            "code": "F41.9",
            "description": "Anxiety disorder, unspecified",
            "primary": True,
        })

    return result


def suggest_cpt_from_duration(duration_minutes: int, modality: str = "individual") -> str:
    """
    Returns the most appropriate CPT code based on session duration and modality.
    """
    if "family" in modality.lower():
        return "90847"
    if "group" in modality.lower():
        return "90853"
    if duration_minutes >= 53:
        return "90837"
    elif duration_minutes >= 38:
        return "90834"
    elif duration_minutes >= 16:
        return "90832"
    else:
        return "90791"  # Evaluation
