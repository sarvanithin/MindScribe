import { AlertTriangle, Phone } from 'lucide-react'

interface RiskAlertProps {
    flags: string[]
}

export default function RiskAlert({ flags }: RiskAlertProps) {
    if (!flags.length) return null

    const hasSI = flags.some(f => f.includes('suicidal'))
    const hasHI = flags.some(f => f.includes('homicidal'))
    const hasSH = flags.some(f => f.includes('self_harm'))

    return (
        <div className="risk-alert">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={15} />
                Safety Concern Detected
            </h3>
            <p style={{ marginBottom: 8 }}>
                This screening detected responses that may indicate safety concerns.
                This tool is <strong>NOT a substitute for clinical judgment.</strong> Immediate clinical review is recommended.
            </p>

            {hasSI && <p style={{ color: '#fca5a5', marginBottom: 4 }}>⚠ Suicidal ideation flagged (Q9 or free-text keyword)</p>}
            {hasHI && <p style={{ color: '#fca5a5', marginBottom: 4 }}>⚠ Homicidal ideation language detected in response</p>}
            {hasSH && <p style={{ color: '#fca5a5', marginBottom: 4 }}>⚠ Self-harm language detected in response</p>}

            <div style={{ borderTop: '1px solid rgba(239,68,68,0.25)', paddingTop: 10, marginTop: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <Phone size={13} style={{ color: '#fca5a5' }} />
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fca5a5' }}>Crisis Resources</span>
                </div>
                <ul>
                    <li>National Suicide Prevention Lifeline: <strong>988</strong> (call or text)</li>
                    <li>Crisis Text Line: Text <strong>HOME</strong> to 741741</li>
                    <li>Emergency: <strong>911</strong></li>
                </ul>
            </div>
        </div>
    )
}
