import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import type { ScreeningHistoryEntry } from '../lib/api'
import { SEVERITY_LABELS } from '../lib/scoring'

interface ScoreTrendProps {
    history: ScreeningHistoryEntry[]
}

export default function ScoreTrend({ history }: ScoreTrendProps) {
    if (!history.length) {
        return (
            <div className="empty-state">
                <p>No screening history yet. Complete a PHQ-9 or GAD-7 to see trends.</p>
            </div>
        )
    }

    // Split by type
    const phq9 = history.filter(h => h.assessment_type === 'PHQ9')
    const gad7 = history.filter(h => h.assessment_type === 'GAD7')

    // Merge for chart (by date)
    const dateMap: Record<string, { date: string; phq9?: number; gad7?: number }> = {}
    phq9.forEach(h => {
        const d = h.completed_at.slice(0, 10)
        dateMap[d] = { ...dateMap[d], date: d, phq9: h.total_score }
    })
    gad7.forEach(h => {
        const d = h.completed_at.slice(0, 10)
        dateMap[d] = { ...dateMap[d], date: d, gad7: h.total_score }
    })
    const chartData = Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date))

    return (
        <div className="card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 20 }}>Score Trends</h3>
            <ResponsiveContainer width="100%" height={240}>
                <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                    <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                    <Tooltip
                        contentStyle={{
                            background: '#1e293b',
                            border: '1px solid rgba(148,163,184,0.2)',
                            borderRadius: 10,
                            fontSize: 12,
                        }}
                    />
                    <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                    {phq9.length > 0 && (
                        <Line
                            type="monotone"
                            dataKey="phq9"
                            name="PHQ-9"
                            stroke="#14b8a6"
                            strokeWidth={2}
                            dot={{ r: 4, fill: '#14b8a6' }}
                            activeDot={{ r: 6 }}
                        />
                    )}
                    {gad7.length > 0 && (
                        <Line
                            type="monotone"
                            dataKey="gad7"
                            name="GAD-7"
                            stroke="#818cf8"
                            strokeWidth={2}
                            dot={{ r: 4, fill: '#818cf8' }}
                            activeDot={{ r: 6 }}
                        />
                    )}
                </LineChart>
            </ResponsiveContainer>

            {/* History table */}
            <div className="divider" />
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                    <thead>
                        <tr style={{ color: 'var(--text-muted)' }}>
                            {['Assessment', 'Score', 'Severity', 'Date', 'Risk Flags'].map(h => (
                                <th key={h} style={{ textAlign: 'left', padding: '6px 12px', fontWeight: 600 }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {history.slice().reverse().map(h => (
                            <tr key={h.session_id} style={{ borderTop: '1px solid var(--border)' }}>
                                <td style={{ padding: '8px 12px' }}>
                                    <span className="code-label">{h.assessment_type}</span>
                                </td>
                                <td style={{ padding: '8px 12px', fontWeight: 700, color: 'var(--text-primary)' }}>
                                    {h.total_score}/{h.max_score}
                                </td>
                                <td style={{ padding: '8px 12px' }}>
                                    <span className={`severity-badge severity-${h.severity}`} style={{ fontSize: '0.65rem' }}>
                                        {SEVERITY_LABELS[h.severity as keyof typeof SEVERITY_LABELS] || h.severity}
                                    </span>
                                </td>
                                <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>
                                    {h.completed_at.slice(0, 10)}
                                </td>
                                <td style={{ padding: '8px 12px', color: h.risk_flags.length ? '#ef4444' : 'var(--text-muted)' }}>
                                    {h.risk_flags.length ? `⚠ ${h.risk_flags.length} flag(s)` : 'None'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
