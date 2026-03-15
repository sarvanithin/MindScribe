type Format = 'DAP' | 'SOAP' | 'BIRP'

interface FormatSelectorProps {
    value: Format
    onChange: (fmt: Format) => void
}

const FORMATS: { value: Format; label: string; desc: string }[] = [
    { value: 'DAP', label: 'DAP', desc: 'Data · Assessment · Plan' },
    { value: 'SOAP', label: 'SOAP', desc: 'Subjective · Objective · Assessment · Plan' },
    { value: 'BIRP', label: 'BIRP', desc: 'Behavior · Intervention · Response · Plan' },
]

export default function FormatSelector({ value, onChange }: FormatSelectorProps) {
    return (
        <div>
            <div className="flex gap-2">
                {FORMATS.map(f => (
                    <button
                        key={f.value}
                        className={`format-pill${value === f.value ? ' active' : ''}`}
                        onClick={() => onChange(f.value)}
                        title={f.desc}
                    >
                        {f.label}
                    </button>
                ))}
            </div>
            <p className="text-xs text-muted mt-2">
                {FORMATS.find(f => f.value === value)?.desc}
            </p>
        </div>
    )
}
