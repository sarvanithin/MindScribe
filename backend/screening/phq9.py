PHQ9_QUESTIONS = [
    {"num": 1, "text": "Little interest or pleasure in doing things", "domain": "anhedonia"},
    {"num": 2, "text": "Feeling down, depressed, or hopeless", "domain": "mood"},
    {"num": 3, "text": "Trouble falling or staying asleep, or sleeping too much", "domain": "sleep"},
    {"num": 4, "text": "Feeling tired or having little energy", "domain": "energy"},
    {"num": 5, "text": "Poor appetite or overeating", "domain": "appetite"},
    {"num": 6, "text": "Feeling bad about yourself — or that you are a failure or have let yourself or your family down", "domain": "self_worth"},
    {"num": 7, "text": "Trouble concentrating on things, such as reading the newspaper or watching television", "domain": "concentration"},
    {"num": 8, "text": "Moving or speaking so slowly that other people could have noticed, or being so fidgety or restless that you have been moving around a lot more than usual", "domain": "psychomotor"},
    {"num": 9, "text": "Thoughts that you would be better off dead, or of hurting yourself in some way", "domain": "suicidal_ideation"},
]

PHQ9_SEVERITY = [
    (0, 4, "minimal"),
    (5, 9, "mild"),
    (10, 14, "moderate"),
    (15, 19, "moderately_severe"),
    (20, 27, "severe"),
]

PHQ9_MAX_SCORE = 27
PHQ9_TOTAL_QUESTIONS = 9


def get_phq9_severity(score: int) -> str:
    for low, high, label in PHQ9_SEVERITY:
        if low <= score <= high:
            return label
    return "severe"
