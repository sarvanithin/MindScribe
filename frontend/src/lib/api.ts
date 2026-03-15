// Typed API wrappers for the MindScribe FastAPI backend

const BASE = '/api'

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    })
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || `API error ${res.status}`)
    }
    return res.json()
}

// ---------------------------------------------------------------------------
// Screening
// ---------------------------------------------------------------------------
export interface StartScreeningResult {
    session_id: string
    question_number: number
    total_questions: number
    question_text: string
    domain: string
    assessment_type: string
}

export interface RespondResult {
    status: 'in_progress' | 'complete'
    question_number: number
    total_questions?: number
    question_text?: string
    domain?: string
    mapped_score: number
    risk_flag?: string | null
    running_total?: number
    result?: {
        total_score: number
        max_score: number
        severity: string
        risk_flags: string[]
        clinical_interpretation: string
        responses: ResponseRecord[]
    }
    crisis_resources?: string
}

export interface ResponseRecord {
    question_number: number
    standard_question: string
    conversational_prompt: string
    patient_response: string
    mapped_score: number
    confidence: number
    notes?: string
    risk_flag?: string | null
    domain: string
}

export interface ScreeningHistoryEntry {
    session_id: string
    assessment_type: string
    total_score: number
    max_score: number
    severity: string
    completed_at: string
    risk_flags: string[]
}

export const api = {
    screening: {
        start: (patientId: string, assessmentType: 'PHQ9' | 'GAD7') =>
            apiFetch<StartScreeningResult>('/screening/start', {
                method: 'POST',
                body: JSON.stringify({ patient_id: patientId, assessment_type: assessmentType }),
            }),

        respond: (sessionId: string, response: string) =>
            apiFetch<RespondResult>('/screening/respond', {
                method: 'POST',
                body: JSON.stringify({ session_id: sessionId, response }),
            }),

        result: (sessionId: string) =>
            apiFetch<RespondResult['result']>(`/screening/result/${sessionId}`),

        history: (patientId: string) =>
            apiFetch<{ patient_id: string; history: ScreeningHistoryEntry[] }>(
                `/screening/history/${patientId}`
            ),
    },

    notes: {
        generate: (payload: {
            transcript: string
            patient_context?: Record<string, unknown>
            format?: 'DAP' | 'SOAP' | 'BIRP'
            session_date?: string
            session_duration?: number
            modality?: string
        }) =>
            apiFetch<{ note: NoteResult }>('/notes/generate', {
                method: 'POST',
                body: JSON.stringify(payload),
            }),
    },

    clinical: {
        icd10: (query?: string) =>
            apiFetch<{ code: string; description: string }[]>(
                `/clinical/icd10${query ? `?query=${encodeURIComponent(query)}` : ''}`
            ),
    },

    demo: {
        transcripts: () => apiFetch<DemoTranscript[]>('/demo/transcripts'),
    },
}

export interface NoteResult {
    id: string
    patient_id: string
    session_date: string
    session_duration: number
    format: string
    modality: string
    sections: Record<string, string>
    diagnosis_codes: { code: string; description: string; primary: boolean }[]
    cpt_code: string
    treatment_goals: string[]
    interventions_used: string[]
    risk_assessment: string
    next_session: string
    full_text: string
}

export interface DemoTranscript {
    id: string
    title: string
    label: string
    diagnosis_hint: string
    session_duration: number
    modality: string
    patient_context: Record<string, unknown>
    text: string
}
