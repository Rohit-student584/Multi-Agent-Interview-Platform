from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import db
from app.agents.resume_agent import analyze_resume


# MongoDB resumes collection
resumes_collection = db["resumes"]


def analyze_saved_resume(
    resume_id: str,
    firebase_uid: str,
    target_role: str = "Software Engineer",
) -> dict:
    """Retrieve a user's resume, analyze it, and save the analysis."""

    # Validate MongoDB ObjectId
    if not ObjectId.is_valid(resume_id):
        raise ValueError("Invalid resume ID.")

    # Find resume belonging to the authenticated user
    resume = resumes_collection.find_one(
        {
            "_id": ObjectId(resume_id),
            "firebase_uid": firebase_uid,
        },
        {
            "filename": 1,
            "extracted_text": 1,
        },
    )

    if resume is None:
        raise LookupError("Resume not found.")

    resume_text = resume.get("extracted_text", "")

    if not resume_text.strip():
        raise ValueError("Resume contains no readable text.")

    # Analyze resume using Gemini AI Agent
    analysis = analyze_resume(
        resume_text=resume_text,
        target_role=target_role,
    )

    now = datetime.now(timezone.utc)

    # Save AI analysis in MongoDB
    resumes_collection.update_one(
        {
            "_id": resume["_id"],
            "firebase_uid": firebase_uid,
        },
        {
            "$set": {
                "analysis": analysis,
                "analysis_target_role": target_role,
                "analysis_updated_at": now,
            }
        },
    )

    return {
        "resume_id": str(resume["_id"]),
        "filename": resume["filename"],
        "target_role": target_role,
        "analysis": analysis,
        "analysis_updated_at": now.isoformat(),
    }