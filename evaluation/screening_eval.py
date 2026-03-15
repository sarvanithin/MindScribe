"""
Screening evaluation: tests that the scorer accurately maps 10 test cases
to their expected PHQ-9/GAD-7 scores.
Run: python -m evaluation.screening_eval
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.screening.scorer import score_response


async def run_eval():
    test_file = Path(__file__).parent / "test_transcripts.json"
    with open(test_file) as f:
        tests = json.load(f)

    screening_tests = [t for t in tests if t.get("type") == "screening"]
    print(f"\n{'='*60}")
    print(f"MindScribe Screening Eval — {len(screening_tests)} test cases")
    print(f"{'='*60}\n")

    passed = 0
    for t in screening_tests:
        result = await score_response(
            assessment_type=t["assessment_type"],
            question_num=t["question_num"],
            domain=t["domain"],
            standard_question=t["standard_question"],
            conversational_prompt=t["conversational_prompt"],
            patient_response=t["patient_response"],
        )
        expected = t["expected_score"]
        actual = result["score"]
        # Allow ±1 tolerance for natural language ambiguity
        ok = abs(actual - expected) <= 1
        if ok:
            passed += 1
        status = "✓ PASS" if ok else "✗ FAIL"
        label = t.get("name") or f"Q{t['question_num']} [{t['domain']}]"
        print(f"{status}  {label}")
        print(f"       Response: '{t['patient_response'][:60]}'")
        print(f"       Expected: {expected} | Got: {actual} | Confidence: {result['confidence']:.2f}")
        if t.get("expect_risk_flag"):
            flag_ok = result.get("risk_flag") is not None
            print(f"       Risk flag: {'✓ detected' if flag_ok else '✗ MISSED'}")
        print()

    pct = int(passed / len(screening_tests) * 100)
    print(f"Result: {passed}/{len(screening_tests)} passed ({pct}%)\n")
    return pct >= 80  # 80% threshold


if __name__ == "__main__":
    ok = asyncio.run(run_eval())
    sys.exit(0 if ok else 1)
