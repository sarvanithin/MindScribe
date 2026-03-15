"""
Async LLM wrapper using Groq API (OpenAI-compatible).
Single call site — swap the model or provider here without touching callers.
"""
from groq import AsyncGroq
from backend.config import GROQ_API_KEY

MODEL = "llama-3.3-70b-versatile"

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=GROQ_API_KEY)
    return _client


async def chat_completion(
    system: str,
    user: str,
    temperature: float = 0.3,
    json_mode: bool = False,
) -> str:
    """
    Returns the assistant message text.
    Raises on API error — callers should catch and fall back to demo.
    """
    client = _get_client()
    kwargs: dict = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
