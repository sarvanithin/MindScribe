import { useState, useRef, useEffect } from 'react'
import { Copy, Check, Download } from 'lucide-react'
import type { NoteResult } from '../lib/api'

interface NoteEditorProps {
    note: NoteResult
}

const SECTION_LABELS: Record<string, string> = {
    data: 'DATA',
    assessment: 'ASSESSMENT',
    plan: 'PLAN',
    subjective: 'SUBJECTIVE',
    objective: 'OBJECTIVE',
    behavior: 'BEHAVIOR',
    intervention: 'INTERVENTION',
    response: 'RESPONSE',
}

export default function NoteEditor({ note }: NoteEditorProps) {
    const [copied, setCopied] = useState(false)
    const [sections, setSections] = useState<Record<string, string>>(note.sections)

    useEffect(() => {
        setSections(note.sections)
    }, [note])

    const handleCopy = async () => {
        await navigator.clipboard.writeText(note.full_text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const handleExport = () => {
        const blob = new Blob([note.full_text], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `session-note-${note.format}-${note.session_date?.replace(/\//g, '-') ?? 'export'}.txt`
        a.click()
        URL.revokeObjectURL(url)
    }

    return (
        <div className="card" style={{ padding: '24px' }}>
            {/* Header row */}
            <div className="flex justify-between items-center">
                <div>
                    <div className="flex gap-2 items-center">
                        <span className="code-label">{note.format}</span>
                        <span className="text-sm text-muted">{note.session_date} · {note.session_duration} min</span>
                    </div>
                    <div className="flex gap-3 mt-2">
                        {note.diagnosis_codes.slice(0, 2).map(dx => (
                            <span key={dx.code} className="text-xs" style={{ color: 'var(--teal-400)' }}>
                                {dx.code}
                            </span>
                        ))}
                        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            CPT {note.cpt_code}
                        </span>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button className="btn btn-ghost btn-sm" onClick={handleExport} id="export-note-btn">
                        <Download size={14} /> Export
                    </button>
                    <button className="btn btn-secondary btn-sm" onClick={handleCopy} id="copy-note-btn">
                        {copied ? <><Check size={14} /> Copied!</> : <><Copy size={14} /> Copy</>}
                    </button>
                </div>
            </div>

            {/* Risk assessment pill */}
            {note.risk_assessment && (
                <div className="mt-3" style={{
                    background: 'rgba(20,184,166,0.08)',
                    border: '1px solid rgba(20,184,166,0.2)',
                    borderRadius: 'var(--radius-md)',
                    padding: '8px 14px',
                    fontSize: '0.8rem',
                    color: 'var(--text-secondary)',
                }}>
                    <strong style={{ color: 'var(--teal-400)' }}>Risk Assessment: </strong>
                    {note.risk_assessment}
                </div>
            )}

            <div className="divider" />

            {/* Editable sections */}
            {Object.entries(sections).map(([key, content]) => (
                <div key={key}>
                    <div className="note-section-header">{SECTION_LABELS[key] || key.toUpperCase()}</div>
                    <textarea
                        className="note-textarea"
                        value={content}
                        onChange={e => setSections(prev => ({ ...prev, [key]: e.target.value }))}
                        rows={Math.max(4, content.split('\n').length + 1)}
                        id={`note-section-${key}`}
                    />
                </div>
            ))}

            <div className="divider" />

            {/* Metadata */}
            <div className="grid-2" style={{ gap: 12 }}>
                <div>
                    <p className="stat-label">Interventions Used</p>
                    <div className="flex-col gap-1 mt-2" style={{ display: 'flex' }}>
                        {note.interventions_used.length
                            ? note.interventions_used.map(i => (
                                <span key={i} className="text-xs" style={{ color: 'var(--text-secondary)' }}>• {i}</span>
                            ))
                            : <span className="text-xs text-muted">Not specified</span>
                        }
                    </div>
                </div>
                <div>
                    <p className="stat-label">Treatment Goals</p>
                    <div className="flex-col gap-1 mt-2" style={{ display: 'flex' }}>
                        {note.treatment_goals.length
                            ? note.treatment_goals.map(g => (
                                <span key={g} className="text-xs" style={{ color: 'var(--text-secondary)' }}>• {g}</span>
                            ))
                            : <span className="text-xs text-muted">Not specified</span>
                        }
                    </div>
                </div>
            </div>
        </div>
    )
}
