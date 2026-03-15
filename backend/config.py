import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() == "true"

# If no API key is set, automatically go into demo mode
if not GROQ_API_KEY:
    DEMO_MODE = True

MODEL_NAME = "llama-3.3-70b-versatile"
