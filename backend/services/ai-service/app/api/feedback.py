
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.services.feedback_service import evaluate_and_save_answer_feedback


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/feedback",
    tags=["AI Interview Feedback"],
)


@router.post("/interviews/{interview_id}/questions/{question_number}")
def generate_answer_feedback(
    interview_id: str,
    question_number: int,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = evaluate_and_save_answer_feedback(
            interview_id=interview_id,
            firebase_uid=firebase_uid,
            question_number=question_number,
        )

        return {
            "success": True,
            "message": "AI feedback generated successfully.",
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

    except Exception as exc:
        logger.exception(
            "AI feedback generation failed for interview %s, question %s",
            interview_id,
            question_number,
        )

        raise HTTPException(
            status_code=502,
            detail="AI feedback generation failed.",
        ) from exc
