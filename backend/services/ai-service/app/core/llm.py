
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

SERVICE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(SERVICE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing from AI Service .env file")

llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.2,
    reasoning_effort="low",
    model_kwargs={
        "include_reasoning": False
    },
)

print(f"Groq LLM initialized successfully: {GROQ_MODEL}")
