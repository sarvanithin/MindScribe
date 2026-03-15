# MindScribe

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green) ![React](https://img.shields.io/badge/React-18+-61DAFB) ![Groq](https://img.shields.io/badge/Groq-Llama--3.3--70B-orange) ![License](https://img.shields.io/badge/license-MIT-blue)

AI-powered clinical documentation tool for mental health professionals. MindScribe conducts conversational PHQ-9 and GAD-7 screenings and generates structured clinical notes (DAP, SOAP, BIRP) from therapy session transcripts — powered by Llama 3.3 70B via Groq.

---

## Screenshots

**Conversational PHQ-9 Screening**

![Screening chat UI showing adaptive conversational questions with running score tracker](docs/screenshot_screening.png)

**Note Generator**

![Note generator showing DAP/SOAP/BIRP format selector with generated clinical note output](docs/screenshot_notes.png)

---

## Features

- **Conversational Screening** — PHQ-9 and GAD-7 as adaptive dialogue, not a checkbox form; questions adjust tone based on prior answers
- **Automatic Scoring** — LLM maps free-text patient responses to 0–3 severity scores per item, with heuristic fallback
- **Risk Detection** — flags suicidal ideation (PHQ-9 Q9) at both keyword and LLM level; always forces a flag on any positive Q9 response
- **Note Generation** — DAP, SOAP, or BIRP notes from session transcripts in seconds
- **ICD-10 & CPT Coding** — suggests diagnosis codes and billing codes automatically
- **Dashboard** — session history, screening trends (Recharts), prior note review
- **Demo Mode** — fully functional without an API key using pre-seeded data

## Quick Start

### Backend

```bash
cd mindscribe
pip install -r requirements.txt

# Set your Groq API key (get one free at console.groq.com)
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Optional: seed demo screening data
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

Without a `GROQ_API_KEY`, the app runs in demo mode automatically — adaptive questions use curated static phrasings and notes use realistic pre-written templates. Run `python scripts/seed_demo.py` first to populate demo screening history.

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
# Screening accuracy (no backend needed)
python -m evaluation.screening_eval
# Expected: >= 80% pass rate

# Note quality (requires backend running on port 8000)
python -m evaluation.note_eval
# Expected: 100% pass rate
```

The evaluation suite tests against `evaluation/test_transcripts.json` — 6 screening cases (PHQ-9 anhedonia severe, PHQ-9 mood moderate, PHQ-9 sleep mild, PHQ-9 suicidal ideation with risk flag, GAD-7 nervousness severe, GAD-7 irritability none) and 4 note generation cases covering all three note formats.

## Clinical Disclaimer

MindScribe is a **research and demonstration tool only**.

- No real patient data should be entered — all data is in-memory and lost on restart
- This system is not HIPAA-compliant infrastructure
- AI-generated notes and scores must be reviewed by a licensed clinician before any clinical use
- PHQ-9 and GAD-7 are validated instruments; this implementation is for workflow demonstration only
