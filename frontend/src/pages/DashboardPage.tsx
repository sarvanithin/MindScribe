import { useState, useEffect } from 'react'
import { LayoutDashboard, TrendingUp, AlertTriangle, Activity } from 'lucide-react'
import { api, type ScreeningHistoryEntry } from '../lib/api'
import ScoreTrend from '../components/ScoreTrend'
import { SEVERITY_LABELS, SEVERITY_COLORS } from '../lib/scoring'

const PATIENT_ID = 'demo-patient-001'

export default function DashboardPage() {
    const [history, setHistory] = useState<ScreeningHistoryEntry[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.screening.history(PATIENT_ID)
            .then(res => setHistory(res.history))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    // Stats
    const phq9History = history.filter(h => h.assessment_type === 'PHQ9')
    const gad7History = history.filter(h => h.assessment_type === 'GAD7')
    const latestPhq9 = phq9History[phq9History.length - 1]
    const latestGad7 = gad7History[gad7History.length - 1]
    const totalRiskFlags = history.reduce((acc, h) => acc + h.risk_flags.length, 0)

    return (
        <div>
            <div className="page-header">
                <h2>Dashboard</h2>
                <p>Patient screening history, score trends, and clinical summary for {PATIENT_ID}</p>
            </div>

            <div className="page-body">
                {loading ? (
                    <div className="empty-state">
                        <span className="spinner" />
                        <p>Loading history...</p>
                    </div>
                ) : (
                    <>
                        {/* Stat cards */}
                        <div className="grid-3" style={{ marginBottom: 24 }}>
                            <div className="stat-card">
                                <p className="stat-label">Latest PHQ-9</p>
                                {latestPhq9 ? (
                                    <>
                                        <p className="stat-value" style={{ color: SEVERITY_COLORS[latestPhq9.severity as keyof typeof SEVERITY_COLORS] ?? 'var(--text-primary)' }}>
                                            {latestPhq9.total_score}
                                        </p>
                                        <span className={`severity-badge severity-${latestPhq9.severity}`} style={{ marginTop: 8, display: 'inline-flex' }}>
                                            {SEVERITY_LABELS[latestPhq9.severity as keyof typeof SEVERITY_LABELS]}
                                        </span>
                                    </>
                                ) : (
                                    <p className="text-sm text-muted mt-2">No PHQ-9 yet</p>
                                )}
                            </div>

                            <div className="stat-card">
                                <p className="stat-label">Latest GAD-7</p>
                                {latestGad7 ? (
                                    <>
                                        <p className="stat-value" style={{ color: SEVERITY_COLORS[latestGad7.severity as keyof typeof SEVERITY_COLORS] ?? 'var(--text-primary)' }}>
                                            {latestGad7.total_score}
                                        </p>
                                        <span className={`severity-badge severity-${latestGad7.severity}`} style={{ marginTop: 8, display: 'inline-flex' }}>
                                            {SEVERITY_LABELS[latestGad7.severity as keyof typeof SEVERITY_LABELS]}
                                        </span>
                                    </>
                                ) : (
                                    <p className="text-sm text-muted mt-2">No GAD-7 yet</p>
                                )}
                            </div>

                            <div className="stat-card">
                                <p className="stat-label">Sessions</p>
                                <p className="stat-value">{history.length}</p>
                                {totalRiskFlags > 0 && (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 8 }}>
                                        <AlertTriangle size={12} style={{ color: '#ef4444' }} />
                                        <span style={{ fontSize: '0.75rem', color: '#f87171' }}>
                                            {totalRiskFlags} risk flag{totalRiskFlags !== 1 ? 's' : ''} across all sessions
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Score trends chart */}
                        <ScoreTrend history={history} />

                        {history.length === 0 && (
                            <div className="empty-state" style={{ marginTop: 24 }}>
                                <Activity size={48} />
                                <h3>No Screening History</h3>
                                <p>
                                    Complete a PHQ-9 or GAD-7 screening in the Screening tab to see results here.
                                    Each completed session is automatically added to this dashboard.
                                </p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}
