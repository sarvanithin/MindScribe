import re
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

RISK_KEYWORDS = [
    "kill myself", "end my life", "better off dead", "suicide",
    "want to die", "don't want to be here", "no reason to live",
    "hurt myself", "self-harm", "cutting", "overdose",
    "hurt someone", "homicidal", "kill", "weapon",
    "not worth living", "disappear forever", "wish i was dead",
]

RISK_RESPONSE = """⚠ IMPORTANT SAFETY NOTICE

This screening has detected responses that may indicate safety concerns.
This tool is NOT a substitute for clinical judgment.

If you or someone you know is in crisis:
• National Suicide Prevention Lifeline: 988 (call or text)
• Crisis Text Line: Text HOME to 741741
• Emergency: Call 911

This flag has been recorded and should be reviewed by a licensed clinician
before the patient's next contact.
"""


def check_risk_flags(text: str) -> list[str]:
    """
    Check free-text response for risk keywords.
    Returns list of risk flag labels found.
    """
    flags: list[str] = []
    normalized = text.lower()
    for keyword in RISK_KEYWORDS:
        if keyword in normalized:
            if "homicidal" in keyword or "hurt someone" in keyword:
                flags.append("homicidal_ideation")
            elif any(k in keyword for k in ["kill myself", "suicide", "end my life",
                                             "want to die", "better off dead",
                                             "no reason to live", "not worth living",
                                             "wish i was dead", "disappear forever",
                                             "don't want to be here"]):
                flags.append("suicidal_ideation")
            else:
                flags.append("self_harm")
    return list(set(flags))
