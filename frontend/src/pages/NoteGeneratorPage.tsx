import { useState, useEffect } from 'react'
import { Wand2, FileText, Loader2 } from 'lucide-react'
import { api, type NoteResult, type DemoTranscript } from '../lib/api'
import FormatSelector from '../components/FormatSelector'
import NoteEditor from '../components/NoteEditor'

type Format = 'DAP' | 'SOAP' | 'BIRP'

export default function NoteGeneratorPage() {
    const [transcript, setTranscript] = useState('')
    const [format, setFormat] = useState<Format>('DAP')
    const [duration, setDuration] = useState(53)
    const [modality, setModality] = useState('individual')
    const [isLoading, setIsLoading] = useState(false)
    const [note, setNote] = useState<NoteResult | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [demoTranscripts, setDemoTranscripts] = useState<DemoTranscript[]>([])

    useEffect(() => {
        api.demo.transcripts().then(setDemoTranscripts).catch(console.error)
    }, [])

    const handleGenerate = async () => {
        if (!transcript.trim()) return
        setIsLoading(true)
        setError(null)
        try {
            const res = await api.notes.generate({
                transcript,
                format,
                session_duration: duration,
                modality,
            })
            setNote(res.note)
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Failed to generate note')
        } finally {
            setIsLoading(false)
        }
    }

    const loadDemo = (t: DemoTranscript) => {
        setTranscript(t.text)
        setDuration(t.session_duration)
        setModality(t.modality)
        setNote(null)
        setError(null)
    }

    return (
        <div>
            <div className="page-header">
                <h2>Session Note Generator</h2>
                <p>Paste a therapy session transcript to generate DAP, SOAP, or BIRP clinical notes</p>
            </div>

            <div className="page-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>
                    {/* Left panel — input */}
                    <div className="flex-col gap-4" style={{ display: 'flex' }}>
                        {/* Demo transcript buttons */}
                        {demoTranscripts.length > 0 && (
                            <div className="card" style={{ padding: '16px 20px' }}>
                                <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 10 }}>
                                    Try a demo transcript:
                                </p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                    {demoTranscripts.map(t => (
                                        <button
                                            key={t.id}
                                            className="btn btn-ghost btn-sm"
                                            onClick={() => loadDemo(t)}
                                            id={`demo-${t.id}`}
                                            style={{ fontSize: '0.75rem' }}
                                        >
                                            <FileText size={12} />
                                            {t.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Transcript input */}
                        <div className="card" style={{ padding: '20px' }}>
                            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>
                                Session Transcript
                            </label>
                            <textarea
                                id="transcript-input"
                                className="input"
                                style={{ minHeight: 300, fontFamily: 'var(--font-sans)', lineHeight: 1.65, resize: 'vertical' }}
                                value={transcript}
                                onChange={e => setTranscript(e.target.value)}
                                placeholder="Paste your therapy session transcript here...&#10;&#10;Therapist: How has your week been?&#10;Patient: Honestly, it's been difficult..."
                            />
                        </div>

                        {/* Config */}
                        <div className="card" style={{ padding: '20px' }}>
                            <div className="flex-col gap-4" style={{ display: 'flex' }}>
                                <div>
                                    <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>
                                        Note Format
                                    </label>
                                    <FormatSelector value={format} onChange={setFormat} />
                                </div>

                                <div className="grid-2">
                                    <div>
                                        <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                                            Duration (min)
                                        </label>
                                        <select
                                            id="duration-select"
                                            className="input select"
                                            value={duration}
                                            onChange={e => setDuration(Number(e.target.value))}
                                        >
                                            <option value={30}>30 min (90832)</option>
                                            <option value={45}>45 min (90834)</option>
                                            <option value={53}>53+ min (90837)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                                            Modality
                                        </label>
                                        <select
                                            id="modality-select"
                                            className="input select"
                                            value={modality}
                                            onChange={e => setModality(e.target.value)}
                                        >
                                            <option value="individual">Individual</option>
                                            <option value="group">Group</option>
                                            <option value="family">Family</option>
                                            <option value="couples">Couples</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <button
                            id="generate-note-btn"
                            className="btn btn-primary btn-lg w-full"
                            onClick={handleGenerate}
                            disabled={!transcript.trim() || isLoading}
                        >
                            {isLoading
                                ? <><Loader2 size={18} style={{ animation: 'spin 0.7s linear infinite' }} /> Generating Note...</>
                                : <><Wand2 size={18} /> Generate {format} Note</>
                            }
                        </button>

                        {error && (
                            <div style={{
                                background: 'rgba(244,63,94,0.1)',
                                border: '1px solid rgba(244,63,94,0.3)',
                                borderRadius: 'var(--radius-md)',
                                padding: '12px 16px',
                                fontSize: '0.85rem',
                                color: '#f87171',
                            }}>
                                {error}
                            </div>
                        )}
                    </div>

                    {/* Right panel — output */}
                    <div>
                        {note ? (
                            <NoteEditor note={note} />
                        ) : (
                            <div className="card empty-state" style={{ padding: '60px 40px' }}>
                                <FileText size={48} style={{ opacity: 0.2 }} />
                                <h3>Note will appear here</h3>
                                <p>
                                    Load a demo transcript or paste your own, select a format, and click Generate.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
