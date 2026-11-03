import os
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials


# Interview Service directory
SERVICE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(SERVICE_DIR / ".env")


def initialize_firebase():
    """Initialize Firebase Admin SDK."""

    try:
        return firebase_admin.get_app()

    except ValueError:
        service_account_path = os.getenv(
            "FIREBASE_SERVICE_ACCOUNT_PATH"
        )

        if not service_account_path:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_PATH is not configured"
            )

        key_path = Path(service_account_path)

        if not key_path.is_absolute():
            key_path = SERVICE_DIR / key_path

        if not key_path.is_file():
            raise RuntimeError(
                "Firebase service account file was not found"
            )

        credential = credentials.Certificate(str(key_path))

        return firebase_admin.initialize_app(credential)


def verify_firebase_token(id_token: str) -> dict:
    """Verify Firebase ID token."""

    app = initialize_firebase()

    return auth.verify_id_token(
        id_token,
        app=app,
    )