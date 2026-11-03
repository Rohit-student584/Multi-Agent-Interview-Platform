
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.schemas.roadmap import (
    RoadmapGenerateRequest,
    RoadmapProgressUpdateRequest,
)
from app.services.roadmap_service import (
    generate_and_save_roadmap,
    get_user_roadmaps,
     update_roadmap_progress,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/roadmaps",
    tags=["AI Career Roadmap"],
)


@router.post("/generate")
def generate_roadmap(
    request: RoadmapGenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = generate_and_save_roadmap(
            firebase_uid=firebase_uid,
            target_role=request.target_role,
            current_skills=request.current_skills,
            experience_level=request.experience_level,
            duration_weeks=request.duration_weeks,
            daily_study_hours=request.daily_study_hours,
        )

        return {
            "success": True,
            "message": "Career roadmap generated successfully.",
            "data": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        logger.exception("Career roadmap generation failed")

        raise HTTPException(
            status_code=502,
            detail="Career roadmap generation failed.",
        ) from exc

@router.get("/my")
def list_my_roadmaps(
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        roadmaps = get_user_roadmaps(firebase_uid)

        return {
            "success": True,
            "count": len(roadmaps),
            "roadmaps": roadmaps,
        }

    except Exception as exc:
        logger.exception("Failed to retrieve user roadmaps")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve roadmaps.",
        ) from exc

@router.patch("/{roadmap_id}/progress")
def update_progress(
    roadmap_id: str,
    request: RoadmapProgressUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = update_roadmap_progress(
            firebase_uid=firebase_uid,
            roadmap_id=roadmap_id,
            week_number=request.week_number,
            completed=request.completed,
        )

        return {
            "success": True,
            "message": "Roadmap progress updated successfully.",
            "data": result,
        }

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
