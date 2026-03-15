# MindScribe

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green) ![React](https://img.shields.io/badge/React-18+-61DAFB) ![Gemini](https://img.shields.io/badge/Gemini-API-orange)

AI-powered clinical documentation tool for mental health professionals. MindScribe conducts conversational PHQ-9 and GAD-7 screenings and generates structured clinical notes (DAP, SOAP, BIRP) from therapy session transcripts.

## Features

- **Conversational Screening** — PHQ-9 and GAD-7 administered as natural dialogue, not a checkbox form
- **Automatic Scoring** — AI maps free-text patient responses to 0–3 severity scores per item
- **Risk Detection** — flags suicidal ideation (PHQ-9 Q9) and triggers crisis resource display
- **Note Generation** — produces DAP, SOAP, or BIRP notes from session transcripts in seconds
- **ICD-10 & CPT Coding** — suggests diagnosis codes and billing codes automatically
- **Dashboard** — session history, screening trends, and prior note review
- **Demo Mode** — works without an API key using pre-seeded demo data

## Quick Start

### Backend

```bash
cd mindscribe
pip install -r requirements.txt

# Optional: set Gemini API key for live AI features
export GEMINI_API_KEY=your_key_here

# Seed demo data (optional)
python scripts/seed_demo.py

# Start server
python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## Demo Mode

The app runs in demo mode when no `GEMINI_API_KEY` is set. All endpoints respond with realistic pre-generated data so the full UI can be exercised without an API key. Run `python scripts/seed_demo.py` first to populate demo screenings.

## API Overview

Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/screening/start` | Start a new PHQ-9 or GAD-7 screening session |
| `POST` | `/screening/respond` | Submit a patient response to the current question |
| `GET` | `/screening/result/{session_id}` | Retrieve completed screening result and score |
| `GET` | `/screening/history/{patient_id}` | Get all past screenings for a patient |
| `POST` | `/notes/generate` | Generate a DAP, SOAP, or BIRP note from a transcript |
| `GET` | `/clinical/icd10` | Search ICD-10 codes (optional `?query=` filter) |
| `GET` | `/demo/transcripts` | List bundled demo session transcripts |

## Evaluation

```bash
# Must have backend running on port 8000 for note eval
python -m uvicorn backend.main:app --port 8000 &

# Screening accuracy (no backend needed)
python -m evaluation.screening_eval
# Expected: >= 80% pass rate

# Note quality
python -m evaluation.note_eval
# Expected: 100% pass rate
```

The evaluation suite lives in `evaluation/` and tests against `evaluation/test_transcripts.json` — 6 screening cases and 4 note generation cases covering all three note formats.

## Clinical Disclaimer

MindScribe is a **research and demonstration tool only**.

- No real patient data should be entered — all data is stored in-memory and lost on restart
- This system is not HIPAA-compliant infrastructure
- AI-generated notes and scores must be reviewed by a licensed clinician before any clinical use
- PHQ-9 and GAD-7 are validated instruments; this implementation is for workflow demonstration only
