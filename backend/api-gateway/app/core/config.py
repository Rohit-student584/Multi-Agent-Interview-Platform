import os
from pathlib import Path

from dotenv import load_dotenv

# Locate the API Gateway's .env file
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

# Microservice URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
RESUME_SERVICE_URL = os.getenv("RESUME_SERVICE_URL")
INTERVIEW_SERVICE_URL = os.getenv("INTERVIEW_SERVICE_URL")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")