import { useState, useRef, useEffect } from 'react'
import { Send, RotateCcw, ChevronRight } from 'lucide-react'
import { api, type RespondResult } from '../lib/api'
import ChatBubble from '../components/ChatBubble'
import ScoreCard from '../components/ScoreCard'
import RiskAlert from '../components/RiskAlert'
import { SEVERITY_LABELS } from '../lib/scoring'

type AssessmentType = 'PHQ9' | 'GAD7'
type Phase = 'select' | 'chat' | 'results'

interface Message {
    role: 'ai' | 'user'
    text: string
}

const PATIENT_ID = 'demo-patient-001'

export default function ScreeningPage() {
    const [phase, setPhase] = useState<Phase>('select')
    const [assessmentType, setAssessmentType] = useState<AssessmentType>('PHQ9')
    const [sessionId, setSessionId] = useState<string>('')
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [questionNum, setQuestionNum] = useState(1)
    const [totalQuestions, setTotalQuestions] = useState(9)
    const [runningScore, setRunningScore] = useState(0)
    const [result, setResult] = useState<RespondResult['result'] | null>(null)
    const [riskFlags, setRiskFlags] = useState<string[]>([])
    const chatRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight
        }
    }, [messages, isLoading])

    const handleStart = async () => {
        setIsLoading(true)
        try {
            const res = await api.screening.start(PATIENT_ID, assessmentType)
            setSessionId(res.session_id)
            setTotalQuestions(res.total_questions)
            setMessages([{ role: 'ai', text: res.question_text }])
            setPhase('chat')
            setQuestionNum(1)
            setRunningScore(0)
            setRiskFlags([])
        } catch (e) {
            console.error(e)
        } finally {
            setIsLoading(false)
        }
    }

    const handleSend = async () => {
        if (!input.trim() || isLoading) return
        const userText = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', text: userText }])
        setIsLoading(true)

        try {
            const res = await api.screening.respond(sessionId, userText)

            if (res.risk_flag) {
                setRiskFlags(prev => [...new Set([...prev, res.risk_flag as string])])
            }

            if (res.status === 'complete' && res.result) {
                setResult(res.result)
                setRiskFlags(res.result.risk_flags)
                setPhase('results')
            } else {
                setMessages(prev => [...prev, { role: 'ai', text: res.question_text! }])
                setQuestionNum(res.question_number)
                setRunningScore(res.running_total ?? 0)
            }
        } catch (e) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: 'I encountered a connection issue. Please check that the backend is running and try again.',
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleReset = () => {
        setPhase('select')
        setMessages([])
        setResult(null)
        setRiskFlags([])
        setInput('')
        setRunningScore(0)
    }

    // ── Select phase ──
    if (phase === 'select') {
        return (
            <div>
                <div className="page-header">
                    <h2>Screening</h2>
                    <p>Conduct a validated PHQ-9 or GAD-7 assessment conversationally</p>
                </div>
                <div className="page-body">
                    <div style={{ maxWidth: 560 }}>
                        <div className="card" style={{ padding: '32px' }}>
                            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8 }}>
                                Select Assessment
                            </h3>
                            <p className="text-sm text-muted" style={{ marginBottom: 24 }}>
                                The AI will guide the patient through each question naturally, adapting
                                tone based on prior responses.
                            </p>

                            <div className="flex-col gap-3" style={{ display: 'flex', marginBottom: 28 }}>
                                {([
                                    { type: 'PHQ9', title: 'PHQ-9', desc: 'Depression screening · 9 questions · Score 0–27', items: ['Anhedonia', 'Mood', 'Sleep', 'Energy', 'Appetite', 'Self-worth', 'Concentration', 'Psychomotor', 'Suicidal ideation'] },
                                    { type: 'GAD7', title: 'GAD-7', desc: 'Anxiety screening · 7 questions · Score 0–21', items: ['Nervousness', 'Worry control', 'Excessive worry', 'Relaxation', 'Restlessness', 'Irritability', 'Fearfulness'] },
                                ] as const).map(opt => (
                                    <button
                                        key={opt.type}
                                        onClick={() => setAssessmentType(opt.type)}
                                        style={{
                                            background: assessmentType === opt.type
                                                ? 'rgba(20,184,166,0.1)'
                                                : 'var(--bg-input)',
                                            border: `1px solid ${assessmentType === opt.type ? 'var(--teal-500)' : 'var(--border)'}`,
                                            borderRadius: 'var(--radius-md)',
                                            padding: '16px 18px',
                                            textAlign: 'left',
                                            cursor: 'pointer',
                                            transition: 'all 0.15s',
                                        }}
                                    >
                                        <div className="flex justify-between items-center">
                                            <span style={{ fontWeight: 700, color: assessmentType === opt.type ? 'var(--teal-400)' : 'var(--text-primary)' }}>
                                                {opt.title}
                                            </span>
                                            {assessmentType === opt.type && <ChevronRight size={16} style={{ color: 'var(--teal-400)' }} />}
                                        </div>
                                        <p className="text-xs text-muted mt-1">{opt.desc}</p>
                                    </button>
                                ))}
                            </div>

                            <div style={{
                                background: 'rgba(30,39,68,0.6)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-md)',
                                padding: '12px 16px',
                                marginBottom: 24,
                                fontSize: '0.8rem',
                                color: 'var(--text-muted)',
                            }}>
                                ⚠ This tool is for demonstration purposes only and is NOT a substitute for clinical assessment by a licensed professional. No data is stored.
                            </div>

                            <button
                                className="btn btn-primary btn-lg w-full"
                                onClick={handleStart}
                                disabled={isLoading}
                                id="start-screening-btn"
                            >
                                {isLoading ? <><span className="spinner" /> Starting...</> : `Start ${assessmentType === 'PHQ9' ? 'PHQ-9' : 'GAD-7'} Screening`}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    // ── Chat phase ──
    if (phase === 'chat') {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
                <div className="page-header" style={{ paddingBottom: 16 }}>
                    <div className="flex justify-between items-center">
                        <div>
                            <h2>{assessmentType === 'PHQ9' ? 'PHQ-9' : 'GAD-7'} Screening</h2>
                            <p className="text-sm text-muted mt-1">
                                Question {questionNum} of {totalQuestions} &nbsp;·&nbsp; Running score: {runningScore}/{assessmentType === 'PHQ9' ? 27 : 21}
                            </p>
                        </div>
                        <button className="btn btn-ghost btn-sm" onClick={handleReset} id="reset-screening-btn">
                            <RotateCcw size={14} /> Reset
                        </button>
                    </div>

                    {/* Progress bar */}
                    <div className="score-gauge-track mt-3" style={{ height: 6 }}>
                        <div
                            className="score-gauge-fill"
                            style={{
                                width: `${((questionNum - 1) / totalQuestions) * 100}%`,
                                background: 'var(--teal-500)',
                                transition: 'width 0.4s ease',
                            }}
                        />
                    </div>

                    {/* Risk alert */}
                    {riskFlags.length > 0 && (
                        <div className="mt-3 page-body" style={{ padding: '0 40px' }}>
                            <RiskAlert flags={riskFlags} />
                        </div>
                    )}
                </div>

                {/* Chat messages */}
                <div
                    ref={chatRef}
                    className="chat-container"
                    style={{ flex: 1, overflowY: 'auto', padding: '0 40px 8px' }}
                >
                    {messages.map((m, i) => (
                        <ChatBubble key={i} role={m.role} text={m.text} />
                    ))}
                    {isLoading && <ChatBubble role="ai" text="" isTyping />}
                </div>

                {/* Input */}
                <div style={{ padding: '12px 40px 20px', borderTop: '1px solid var(--border)', background: 'var(--bg-app)' }}>
                    <div className="flex gap-2">
                        <input
                            id="screening-input"
                            className="input"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                            placeholder="Type your response..."
                            disabled={isLoading}
                            autoFocus
                        />
                        <button
                            id="screening-send-btn"
                            className="btn btn-primary"
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                        >
                            <Send size={16} />
                        </button>
                    </div>
                    <p className="text-xs text-muted mt-2">
                        Press Enter to send · Your responses are not saved or transmitted beyond this session
                    </p>
                </div>
            </div>
        )
    }

    // ── Results phase ──
    return (
        <div>
            <div className="page-header">
                <div className="flex justify-between items-center">
                    <div>
                        <h2>Screening Complete</h2>
                        <p>{assessmentType === 'PHQ9' ? 'PHQ-9 Depression' : 'GAD-7 Anxiety'} Screening Results</p>
                    </div>
                    <div className="flex gap-2">
                        <button className="btn btn-ghost btn-sm" onClick={handleReset} id="new-screening-btn">
                            <RotateCcw size={14} /> New Screening
                        </button>
                    </div>
                </div>
            </div>
            <div className="page-body">
                {riskFlags.length > 0 && (
                    <div style={{ marginBottom: 20 }}>
                        <RiskAlert flags={riskFlags} />
                    </div>
                )}

                {result && (
                    <ScoreCard
                        assessmentType={assessmentType}
                        totalScore={result.total_score}
                        maxScore={result.max_score}
                        severity={result.severity}
                        responses={result.responses}
                        interpretation={result.clinical_interpretation}
                    />
                )}
            </div>
        </div>
    )
}
