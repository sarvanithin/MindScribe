GAD7_QUESTIONS = [
    {"num": 1, "text": "Feeling nervous, anxious, or on edge", "domain": "nervousness"},
    {"num": 2, "text": "Not being able to stop or control worrying", "domain": "worry"},
    {"num": 3, "text": "Worrying too much about different things", "domain": "excessive_worry"},
    {"num": 4, "text": "Trouble relaxing", "domain": "relaxation"},
    {"num": 5, "text": "Being so restless that it is hard to sit still", "domain": "restlessness"},
    {"num": 6, "text": "Becoming easily annoyed or irritable", "domain": "irritability"},
    {"num": 7, "text": "Feeling afraid, as if something awful might happen", "domain": "fear"},
]

GAD7_SEVERITY = [
    (0, 4, "minimal"),
    (5, 9, "mild"),
    (10, 14, "moderate"),
    (15, 21, "severe"),
]

GAD7_MAX_SCORE = 21
GAD7_TOTAL_QUESTIONS = 7


def get_gad7_severity(score: int) -> str:
    for low, high, label in GAD7_SEVERITY:
        if low <= score <= high:
            return label
    return "severe"
