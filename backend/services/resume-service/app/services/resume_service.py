from datetime import datetime, timezone

from app.core.database import db


# MongoDB resumes collection
resumes_collection = db["resumes"]


def create_resume_record(
    firebase_uid: str,
    filename: str,
    file_type: str,
    extracted_text: str,
) -> dict:
    """Save extracted resume data in MongoDB Atlas."""

    now = datetime.now(timezone.utc)

    resume_data = {
        "firebase_uid": firebase_uid,
        "filename": filename,
        "file_type": file_type,
        "extracted_text": extracted_text,
        "extracted_characters": len(extracted_text),
        "created_at": now,
        "updated_at": now,
    }

    result = resumes_collection.insert_one(resume_data)

    return {
        "id": str(result.inserted_id),
        "filename": filename,
        "file_type": file_type,
        "extracted_characters": len(extracted_text),
        "created_at": now.isoformat(),
    }

def get_user_resumes(firebase_uid: str) -> list[dict]:
    """Return the authenticated user's saved resumes."""

    documents = resumes_collection.find(
        {"firebase_uid": firebase_uid},
        {"extracted_text": 0},
    ).sort("created_at", -1)

    resumes = []

    for document in documents:
        created_at = document.get("created_at")

        resumes.append({
            "id": str(document["_id"]),
            "filename": document["filename"],
            "file_type": document["file_type"],
            "extracted_characters": document["extracted_characters"],
            "created_at": (
                created_at.isoformat()
                if created_at
                else None
            ),
        })

    return resumes