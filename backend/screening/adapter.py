"""
Adapter: uses Gemini (or demo fallback) to rephrase clinical PHQ/GAD questions
into warm, conversational language that adapts to prior responses.
"""
from backend.config import DEMO_MODE
from backend.notes.prompts import ADAPTER_SYSTEM, ADAPTER_PROMPT
from backend.llm import chat_completion

# ---------------------------------------------------------------------------
# Demo fallbacks — clinically appropriate adaptive phrasings for each domain
# ---------------------------------------------------------------------------
DEMO_PHRASINGS: dict[str, list[str]] = {
    "anhedonia": [
        "I'd like to check in on how you've been feeling lately. Over the past couple of weeks, have you noticed a loss of interest or pleasure in activities you usually enjoy?",
        "Have you been finding it hard to enjoy things you normally like — hobbies, spending time with people, that kind of thing?",
    ],
    "mood": [
        "In the past two weeks, have you been feeling down, depressed, or hopeless at all — even just some of the time?",
        "You mentioned feeling less interested in things lately. Has that come along with feeling down or hopeless? Even just occasionally?",
    ],
    "sleep": [
        "How has your sleep been over the past two weeks? Have you had trouble falling asleep, staying asleep, or found yourself sleeping much more than usual?",
        "Sleep is often connected to how we're feeling overall — have you noticed any changes in your sleep patterns lately?",
    ],
    "energy": [
        "Have you been feeling tired or having little energy over the past two weeks, even when you haven't done much?",
        "Along with the sleep changes, have you been feeling physically drained or low on energy during the day?",
    ],
    "appetite": [
        "Have you noticed any changes in your appetite or eating habits over the past two weeks — either eating much less or much more than usual?",
        "Sometimes when we're struggling emotionally, our eating patterns shift. Has that been the case for you recently?",
    ],
    "self_worth": [
        "This next one can be a bit personal, and I want you to know there's no judgement here. Over the past two weeks, have you had feelings of being down on yourself — like you've let yourself or others down, or feelings of worthlessness?",
        "Have you been having any critical thoughts about yourself lately — like feeling like a failure or that you've been letting people down?",
    ],
    "concentration": [
        "Over the past two weeks, have you had trouble focusing or concentrating — whether on work, reading, watching something, or even just everyday tasks?",
        "Along with the low energy, have you noticed it's harder to concentrate or stay focused than usual?",
    ],
    "psychomotor": [
        "This one is about physical pace. Over the past two weeks, have others commented that you seem to be moving or speaking more slowly than usual? Or on the other hand, have you felt unusually restless or fidgety?",
        "Have you noticed any changes in how quickly you move or speak — feeling slowed down, or alternatively more physically restless than usual?",
    ],
    "suicidal_ideation": [
        "I want to ask you something important, and I hope you'll feel comfortable being honest. Over the past two weeks, have you had any thoughts that you'd be better off dead, or any thoughts of hurting yourself in any way?",
        "I need to ask one more question, and I ask everyone this — it's a routine part of the screening. Have you had any thoughts of harming yourself or not wanting to be here over the past two weeks?",
    ],
    # GAD-7 domains
    "nervousness": [
        "Over the past two weeks, how often have you been feeling nervous, anxious, or on edge?",
        "Let's check in on anxiety. In the past two weeks, have you felt particularly nervous or on edge?",
    ],
    "worry": [
        "Have you found it hard to stop or control your worrying over the past two weeks — like your mind keeps going even when you try to stop?",
        "Along with feeling on edge, have you been having trouble stopping yourself from worrying once it starts?",
    ],
    "excessive_worry": [
        "Have you been worrying a lot about many different things over the past two weeks — not just one specific concern but across different areas of your life?",
        "Has the worrying been about lots of different things — work, relationships, health, or just general 'what if' thinking?",
    ],
    "relaxation": [
        "Have you been having trouble relaxing over the past two weeks, even when you have downtime or try to unwind?",
        "Even during times that should feel calm, have you found it hard to actually relax and let go of tension?",
    ],
    "restlessness": [
        "Over the past two weeks, have you felt so restless that it's been hard to sit still — like you need to be moving or doing something?",
        "Has the anxiety come with physical restlessness — feeling like you can't sit still or settle?",
    ],
    "irritability": [
        "Have you been feeling more easily annoyed or irritable than usual over the past two weeks — perhaps snapping at people or feeling frustrated more quickly?",
        "Sometimes anxiety comes with a short fuse. Have you been more easily irritated or quick to feel frustrated lately?",
    ],
    "fear": [
        "Finally, over the past two weeks, have you had a sense of dread or felt afraid — like something awful might happen, even without a specific reason?",
        "Have you experienced any feelings of fear or a sense that something bad is about to happen, even when things are objectively okay?",
    ],
}


def _get_demo_phrasing(domain: str, question_num: int) -> str:
    phrasings = DEMO_PHRASINGS.get(domain, [])
    if not phrasings:
        return f"Over the past two weeks, how often have you been experiencing: {domain.replace('_', ' ')}?"
    # Alternate between available phrasings based on question number
    return phrasings[question_num % len(phrasings)]


async def get_conversational_question(
    assessment_type: str,
    question_num: int,
    total_questions: int,
    standard_question: str,
    domain: str,
    prior_context: str,
) -> str:
    """
    Returns a conversational version of a PHQ/GAD question.
    Uses Gemini if available, otherwise returns a high-quality demo phrasing.
    """
    if DEMO_MODE:
        return _get_demo_phrasing(domain, question_num)

    try:
        prompt = ADAPTER_PROMPT.format(
            assessment_type=assessment_type,
            question_num=question_num,
            total_questions=total_questions,
            standard_question=standard_question,
            domain=domain,
            prior_context=prior_context or "None — this is the first question.",
        )
        return await chat_completion(system=ADAPTER_SYSTEM, user=prompt, temperature=0.4)
    except Exception as e:
        print(f"[Adapter] Groq error: {e} — using demo fallback")
        return _get_demo_phrasing(domain, question_num)
