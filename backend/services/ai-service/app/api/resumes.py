from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.services.resume_analysis_service import analyze_saved_resume
from app.services.analysis_retrieval_service import get_saved_resume_analysis


router = APIRouter(
    prefix="/resumes",
    tags=["AI Resume Analysis"],
)


class ResumeAnalysisRequest(BaseModel):
    target_role: str = Field(
        default="Software Engineer",
        min_length=2,
        max_length=100,
    )


@router.post("/{resume_id}/analyze")
def analyze_user_resume(
    resume_id: str,
    request: ResumeAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = analyze_saved_resume(
            resume_id=resume_id,
            firebase_uid=firebase_uid,
            target_role=request.target_role,
        )

        return {
            "success": True,
            "message": "Resume analyzed successfully.",
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

@router.get("/{resume_id}/analysis")
def get_resume_analysis(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = get_saved_resume_analysis(
            resume_id=resume_id,
            firebase_uid=firebase_uid,
        )

        return {
            "success": True,
            "message": "Resume analysis retrieved successfully.",
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