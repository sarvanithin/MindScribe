"""
Seed demo: pre-seeds the in-memory patient history with sample PHQ-9/GAD-7
scores so the Dashboard page shows trend data immediately on load.
Run this against a running MindScribe backend:
  python scripts/seed_demo.py
"""
import requests
import time

BASE = "http://localhost:8000/api"
PATIENT_ID = "demo-patient-001"

SEED_SCREENINGS = [
    # (type, simulated_responses)
    ("PHQ9", ["nearly every day", "yes most days", "I can't sleep most nights",
              "I'm exhausted constantly", "I haven't been eating much",
              "I feel worthless", "I can't concentrate on anything",
              "I'm moving slowly I think", "no thoughts of harming myself"]),
    ("PHQ9", ["sometimes", "a bit down", "I sleep okay mostly",
              "some days I'm tired", "appetite is mostly fine",
              "I feel okay about myself", "a little trouble focusing",
              "nothing unusual", "no"]),
    ("GAD7", ["yes quite often", "it's hard to stop worrying",
              "I worry about everything", "I can't relax",
              "I feel very restless", "I get irritable easily",
              "yes I feel dread sometimes"]),
]


def seed():
    print(f"Seeding demo data for patient: {PATIENT_ID}")
    for assessment_type, responses in SEED_SCREENINGS:
        print(f"\nStarting {assessment_type} screening...")
        # Start
        r = requests.post(f"{BASE}/screening/start", json={
            "patient_id": PATIENT_ID,
            "assessment_type": assessment_type,
        })
        r.raise_for_status()
        data = r.json()
        session_id = data["session_id"]
        print(f"  Session: {session_id}")

        # Answer all questions
        for i, response_text in enumerate(responses):
            result = requests.post(f"{BASE}/screening/respond", json={
                "session_id": session_id,
                "response": response_text,
            })
            result.raise_for_status()
            resp_data = result.json()
            print(f"  Q{i+1}: '{response_text[:30]}...' → {resp_data.get('mapped_score', '?')}")
            if resp_data.get("status") == "complete":
                total = resp_data["result"]["total_score"]
                severity = resp_data["result"]["severity"]
                print(f"  ✓ Complete! Score: {total} | Severity: {severity}")
                break
            time.sleep(0.1)

    print(f"\nDone. Visit /dashboard to see trend charts.")


if __name__ == "__main__":
    seed()
