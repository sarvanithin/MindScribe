import { SEVERITY_LABELS, SEVERITY_COLORS, type Severity } from '../lib/scoring'

interface ScoreCardProps {
    assessmentType: 'PHQ9' | 'GAD7'
    totalScore: number
    maxScore: number
    severity: string
    responses: {
        domain: string
        mapped_score: number
        risk_flag?: string | null
    }[]
    interpretation?: string
}

const DOMAIN_LABELS: Record<string, string> = {
    anhedonia: 'Anhedonia',
    mood: 'Depressed Mood',
    sleep: 'Sleep',
    energy: 'Energy',
    appetite: 'Appetite',
    self_worth: 'Self-Worth',
    concentration: 'Concentration',
    psychomotor: 'Psychomotor',
    suicidal_ideation: 'Suicidal Ideation',
    nervousness: 'Nervousness',
    worry: 'Worry Control',
    excessive_worry: 'Excessive Worry',
    relaxation: 'Relaxation',
    restlessness: 'Restlessness',
    irritability: 'Irritability',
    fear: 'Fearfulness',
}

function scoreColor(score: number, max: number): string {
    const pct = score / max
    if (pct < 0.2) return '#4ade80'
    if (pct < 0.4) return '#fbbf24'
    if (pct < 0.6) return '#fb923c'
    if (pct < 0.8) return '#f87171'
    return '#ef4444'
}

export default function ScoreCard({
    assessmentType, totalScore, maxScore, severity, responses, interpretation
}: ScoreCardProps) {
    const sev = severity as Severity
    const gaugePct = Math.min(100, Math.round((totalScore / maxScore) * 100))
    const sevColor = SEVERITY_COLORS[sev] || '#94a3b8'

    return (
        <div className="card" style={{ padding: '24px' }}>
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>
                        {assessmentType === 'PHQ9' ? 'PHQ-9' : 'GAD-7'} Results
                    </h3>
                    <p className="text-sm text-muted mt-1">Depression & Mood Screening</p>
                </div>
                <div className={`severity-badge severity-${severity}`}>
                    {SEVERITY_LABELS[sev] || severity}
                </div>
            </div>

            {/* Score */}
            <div className="flex items-center gap-4 mt-4">
                <div>
                    <span style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-0.04em', color: sevColor }}>
                        {totalScore}
                    </span>
                    <span style={{ fontSize: '1rem', color: 'var(--text-muted)', marginLeft: 4 }}>
                        / {maxScore}
                    </span>
                </div>
            </div>

            {/* Gauge */}
            <div className="score-gauge-track mt-3">
                <div
                    className="score-gauge-fill"
                    style={{ width: `${gaugePct}%`, background: sevColor }}
                />
            </div>
            <div className="flex justify-between mt-1" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>0 – Minimal</span>
                <span>Severe – {maxScore}</span>
            </div>

            {/* Domain breakdown */}
            <div className="divider" />
            <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 12 }}>
                Domain Breakdown
            </h4>
            <div className="flex-col gap-2" style={{ display: 'flex' }}>
                {responses.map((r) => (
                    <div key={r.domain} className="domain-bar">
                        <span style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', width: 130, flexShrink: 0 }}>
                            {DOMAIN_LABELS[r.domain] || r.domain}
                        </span>
                        <div className="domain-bar-track">
                            <div
                                className="domain-bar-fill"
                                style={{
                                    width: `${(r.mapped_score / 3) * 100}%`,
                                    background: scoreColor(r.mapped_score, 3),
                                }}
                            />
                        </div>
                        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', width: 32 }}>
                            {r.mapped_score}/3
                        </span>
                        {r.risk_flag && (
                            <span style={{ fontSize: '0.7rem', color: '#ef4444', fontWeight: 700 }}>⚠</span>
                        )}
                    </div>
                ))}
            </div>

            {/* Interpretation */}
            {interpretation && (
                <>
                    <div className="divider" />
                    <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
                        Clinical Interpretation
                    </h4>
                    <p style={{ fontSize: '0.85rem', lineHeight: 1.65, color: 'var(--text-primary)' }}>
                        {interpretation}
                    </p>
                </>
            )}
        </div>
    )
}
