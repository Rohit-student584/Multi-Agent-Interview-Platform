from bson import ObjectId

from app.core.database import db


# MongoDB resumes collection
resumes_collection = db["resumes"]


def get_saved_resume_analysis(
    resume_id: str,
    firebase_uid: str,
) -> dict:
    """Retrieve a user's previously saved resume analysis."""

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
            "analysis": 1,
            "analysis_target_role": 1,
            "analysis_updated_at": 1,
        },
    )

    if resume is None:
        raise LookupError("Resume not found.")

    analysis = resume.get("analysis")

    if not analysis:
        raise LookupError("Resume analysis not found.")

    updated_at = resume.get("analysis_updated_at")

    return {
        "resume_id": str(resume["_id"]),
        "filename": resume["filename"],
        "target_role": resume.get("analysis_target_role"),
        "analysis": analysis,
        "analysis_updated_at": (
            updated_at.isoformat() if updated_at else None
        ),
    }