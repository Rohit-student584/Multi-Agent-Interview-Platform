
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.agents.interview_agent import generate_interview_questions
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import db

router = APIRouter(
    prefix="/interviews",
    tags=["AI Interview"],
)


class InterviewQuestionGenerationRequest(BaseModel):
    interview_type: Literal["HR", "Technical", "Coding"]

    target_role: str = Field(
        min_length=2,
        max_length=100,
    )

    difficulty: Literal[
        "Beginner",
        "Intermediate",
        "Advanced",
    ] = "Beginner"

    total_questions: int = Field(
        default=5,
        ge=1,
        le=20,
    )


@router.post("/questions/generate")
def generate_questions(
    request: InterviewQuestionGenerationRequest,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = generate_interview_questions(
            interview_type=request.interview_type,
            target_role=request.target_role,
            difficulty=request.difficulty,
            total_questions=request.total_questions,
        )

        return {
            "success": True,
            "message": "Interview questions generated successfully.",
            "firebase_uid": firebase_uid,
            "data": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="AI interview question generation failed.",
        ) from exc

@router.post("/sessions/{interview_id}/generate")
def generate_session_questions(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    if not ObjectId.is_valid(interview_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid interview ID.",
        )

    collection = db["interviews"]

    interview = collection.find_one({
        "_id": ObjectId(interview_id),
        "firebase_uid": firebase_uid,
    })

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    # Return existing questions if generation already succeeded.
    if interview.get("questions") and interview.get("status") == "in_progress":
        questions = interview["questions"]

    else:
        if interview.get("status") != "created":
            raise HTTPException(
                status_code=409,
                detail="This interview session cannot be started.",
            )

        try:
            generated = generate_interview_questions(
                interview_type=interview["interview_type"],
                target_role=interview["target_role"],
                difficulty=interview["difficulty"],
                total_questions=interview["total_questions"],
            )

            questions = generated["questions"]

            if len(questions) != interview["total_questions"]:
                raise ValueError(
                    "Generated question count does not match the session."
                )

            result = collection.update_one(
                {
                    "_id": interview["_id"],
                    "firebase_uid": firebase_uid,
                    "status": "created",
                },
                {
                    "$set": {
                        "questions": questions,
                        "current_question_index": 0,
                        "status": "in_progress",
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

            if result.modified_count != 1:
                raise HTTPException(
                    status_code=409,
                    detail="Interview session changed. Please refresh.",
                )

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="AI question generation failed.",
            ) from exc

    # Never expose expected answers or evaluation criteria here.
    public_questions = [
        {
            "question_number": question["question_number"],
            "question": question["question"],
            "topic": question["topic"],
            "sample_input": question.get("sample_input"),
            "sample_output": question.get("sample_output"),
        }
        for question in questions
    ]

    return {
        "success": True,
        "message": "Interview questions generated successfully.",
        "data": {
            "id": str(interview["_id"]),
            "interview_type": interview["interview_type"],
            "target_role": interview["target_role"],
            "difficulty": interview["difficulty"],
            "total_questions": interview["total_questions"],
            "current_question_index": 0,
            "status": "in_progress",
            "questions": public_questions,
        },
    }
