// Client-side PHQ-9 / GAD-7 scoring utilities

export type Severity = 'minimal' | 'mild' | 'moderate' | 'moderately_severe' | 'severe'

export const PHQ9_THRESHOLDS: [number, number, Severity][] = [
    [0, 4, 'minimal'],
    [5, 9, 'mild'],
    [10, 14, 'moderate'],
    [15, 19, 'moderately_severe'],
    [20, 27, 'severe'],
]

export const GAD7_THRESHOLDS: [number, number, Severity][] = [
    [0, 4, 'minimal'],
    [5, 9, 'mild'],
    [10, 14, 'moderate'],
    [15, 21, 'severe'],
]

export function getPhq9Severity(score: number): Severity {
    for (const [lo, hi, label] of PHQ9_THRESHOLDS) {
        if (score >= lo && score <= hi) return label
    }
    return 'severe'
}

export function getGad7Severity(score: number): Severity {
    for (const [lo, hi, label] of GAD7_THRESHOLDS) {
        if (score >= lo && score <= hi) return label
    }
    return 'severe'
}

export const SEVERITY_LABELS: Record<Severity, string> = {
    minimal: 'Minimal',
    mild: 'Mild',
    moderate: 'Moderate',
    moderately_severe: 'Moderately Severe',
    severe: 'Severe',
}

export const SEVERITY_COLORS: Record<Severity, string> = {
    minimal: '#4ade80',
    mild: '#fbbf24',
    moderate: '#fb923c',
    moderately_severe: '#f87171',
    severe: '#ef4444',
}

export function severityToPercent(score: number, maxScore: number): number {
    return Math.min(100, Math.round((score / maxScore) * 100))
}
