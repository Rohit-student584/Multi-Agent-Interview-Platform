
from datetime import datetime, timezone

from app.core.database import db
from app.agents.roadmap_agent import generate_career_roadmap
from bson import ObjectId

# MongoDB roadmaps collection
roadmaps_collection = db["roadmaps"]


def generate_and_save_roadmap(
    firebase_uid: str,
    target_role: str,
    current_skills: list[str],
    experience_level: str,
    duration_weeks: int,
    daily_study_hours: float,
) -> dict:
    """Generate a personalized roadmap and save it in MongoDB."""

    if not firebase_uid:
        raise ValueError("User ID cannot be empty.")

    # Generate roadmap using the AI Roadmap Agent
    roadmap = generate_career_roadmap(
        target_role=target_role,
        current_skills=current_skills,
        experience_level=experience_level,
        duration_weeks=duration_weeks,
        daily_study_hours=daily_study_hours,
    )

    now = datetime.now(timezone.utc)

    # Prepare roadmap document
    roadmap_document = {
        "firebase_uid": firebase_uid,
        "target_role": target_role,
        "current_skills": current_skills,
        "experience_level": experience_level,
        "duration_weeks": duration_weeks,
        "daily_study_hours": daily_study_hours,
        "roadmap": roadmap,
        "created_at": now,
        "updated_at": now,
        "completed_weeks": [],
    }

    # Save roadmap in MongoDB
    result = roadmaps_collection.insert_one(roadmap_document)

    return {
        "id": str(result.inserted_id),
        "created_at": now.isoformat(),
        **roadmap,
    }

def get_user_roadmaps(firebase_uid: str) -> list[dict]:
    """Retrieve all saved roadmaps belonging to a user."""

    documents = roadmaps_collection.find(
        {"firebase_uid": firebase_uid}
    ).sort("created_at", -1)

    roadmaps = []

    for document in documents:
        roadmap_data = document["roadmap"]

        roadmaps.append({
            "id": str(document["_id"]),
            "target_role": document["target_role"],
            "experience_level": document["experience_level"],
            "duration_weeks": document["duration_weeks"],
            "daily_study_hours": document["daily_study_hours"],
            "created_at": (
                document["created_at"].isoformat()
                if document.get("created_at")
                else None
            ),
            "roadmap": roadmap_data,
            "completed_weeks": sorted(
    document.get("completed_weeks", [])
),
"completed_count": len(
    document.get("completed_weeks", [])
),
"progress_percentage": round(
    (
        len(document.get("completed_weeks", []))
        / document["duration_weeks"]
    ) * 100,
    2,
),
        })

    return roadmaps

def update_roadmap_progress(
    firebase_uid: str,
    roadmap_id: str,
    week_number: int,
    completed: bool,
) -> dict:
    """Update the completion status of a roadmap week."""

    if not ObjectId.is_valid(roadmap_id):
        raise ValueError("Invalid roadmap ID.")

    roadmap = roadmaps_collection.find_one({
        "_id": ObjectId(roadmap_id),
        "firebase_uid": firebase_uid,
    })

    if roadmap is None:
        raise LookupError("Roadmap not found.")

    duration = roadmap["duration_weeks"]

    if week_number < 1 or week_number > duration:
        raise ValueError("Invalid roadmap week number.")

    now = datetime.now(timezone.utc)

    update_operation = {
        "$set": {
            "updated_at": now,
        }
    }

    if completed:
        update_operation["$addToSet"] = {
            "completed_weeks": week_number,
        }
    else:
        update_operation["$pull"] = {
            "completed_weeks": week_number,
        }

    roadmaps_collection.update_one(
        {
            "_id": ObjectId(roadmap_id),
            "firebase_uid": firebase_uid,
        },
        update_operation,
    )

    updated_roadmap = roadmaps_collection.find_one({
        "_id": ObjectId(roadmap_id),
        "firebase_uid": firebase_uid,
    })

    completed_weeks = sorted(
        updated_roadmap.get("completed_weeks", [])
    )

    completed_count = len(completed_weeks)

    return {
        "roadmap_id": roadmap_id,
        "completed_weeks": completed_weeks,
        "total_weeks": duration,
        "completed_count": completed_count,
        "progress_percentage": round(
            (completed_count / duration) * 100, 2
        ),
    }
