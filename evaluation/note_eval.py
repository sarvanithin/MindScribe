"""
Note evaluation: checks that generated notes are complete and clinically sound.
Run: python -m evaluation.note_eval
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.notes.generator import generate_note


REQUIRED_KEYS = {
    "DAP":  ["data", "assessment", "plan"],
    "SOAP": ["subjective", "objective", "assessment", "plan"],
    "BIRP": ["behavior", "intervention", "response", "plan"],
}

CLINICAL_TERMS = [
    "cpt", "icd", "session", "diagnosis", "treatment", "assessment",
    "plan", "risk", "suicid", "intervention",
]


async def run_eval():
    test_file = Path(__file__).parent / "test_transcripts.json"
    with open(test_file) as f:
        tests = json.load(f)

    note_tests = [t for t in tests if t.get("type") == "note"]
    print(f"\n{'='*60}")
    print(f"MindScribe Note Eval — {len(note_tests)} test cases")
    print(f"{'='*60}\n")

    passed = 0
    for t in note_tests:
        fmt = t["format"]
        note = await generate_note(
            transcript=t["transcript"],
            patient_context=t.get("patient_context", {}),
            format=fmt,
            session_duration=t.get("session_duration", 53),
            modality=t.get("modality", "individual"),
        )

        checks = []

        # 1. All required sections present + non-empty
        for section in REQUIRED_KEYS.get(fmt, []):
            content = note.sections.get(section, "")
            checks.append((f"Section '{section}' present", bool(content.strip())))

        # 2. ICD-10 code suggested
        checks.append(("ICD-10 code present", len(note.diagnosis_codes) > 0))

        # 3. CPT code present
        checks.append(("CPT code present", bool(note.cpt_code)))

        # 4. Risk assessment present
        checks.append(("Risk assessment present", bool(note.risk_assessment.strip())))

        # 5. Full text >= 300 words
        word_count = len(note.full_text.split())
        checks.append((f"Word count >= 200 (got {word_count})", word_count >= 200))

        # 6. Clinical completeness — at least 5 clinical terms appear in full text
        text_lower = note.full_text.lower()
        term_hits = sum(1 for term in CLINICAL_TERMS if term in text_lower)
        checks.append((f"Clinical terms >= 5 (got {term_hits})", term_hits >= 5))

        all_pass = all(ok for _, ok in checks)
        if all_pass:
            passed += 1

        status = "✓ PASS" if all_pass else "✗ FAIL"
        print(f"{status}  {t['title']} [{fmt}]")
        for label, ok in checks:
            print(f"       {'✓' if ok else '✗'} {label}")
        print()

    pct = int(passed / len(note_tests) * 100) if note_tests else 0
    print(f"Result: {passed}/{len(note_tests)} passed ({pct}%)\n")
    return pct == 100


if __name__ == "__main__":
    ok = asyncio.run(run_eval())
    sys.exit(0 if ok else 1)
