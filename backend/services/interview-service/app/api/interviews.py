from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewQuestionsSaveRequest,
     InterviewAnswerSubmit,
)
from app.services.interview_service import (
    create_interview_session,
    get_user_interviews,
    save_interview_questions,
    get_interview_session,
     submit_interview_answer,
      get_interview_results,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


@router.post(
    "",
    response_model=InterviewSessionResponse,
    status_code=201,
)
def create_new_interview(
    interview_data: InterviewSessionCreate,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = create_interview_session(
            firebase_uid=firebase_uid,
            interview_data=interview_data.model_dump(),
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to create interview session.",
        ) from exc


@router.get("/my")
def list_my_interviews(
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    interviews = get_user_interviews(firebase_uid)

    return {
        "success": True,
        "count": len(interviews),
        "interviews": interviews,
    }
@router.post("/{interview_id}/questions")
def save_generated_questions(
    interview_id: str,
    request: InterviewQuestionsSaveRequest,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        questions = [
            question.model_dump()
            for question in request.questions
        ]

        result = save_interview_questions(
            interview_id=interview_id,
            firebase_uid=firebase_uid,
            questions=questions,
        )

        return {
            "success": True,
            "message": "Interview questions saved successfully.",
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
    
@router.get("/{interview_id}")
def get_interview_details(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        interview = get_interview_session(
            interview_id=interview_id,
            firebase_uid=firebase_uid,
        )

        # Only expose candidate-facing questions.
        # Never return expected answers or evaluation criteria.
        questions = [
            {
                "question_number": question["question_number"],
                "question": question["question"],
                "topic": question["topic"],
                "sample_input": question.get("sample_input"),
                "sample_output": question.get("sample_output"),
            }
            for question in interview.get("questions", [])
        ]

        return {
            "success": True,
            "message": "Interview session retrieved successfully.",
            "data": {
                "id": str(interview["_id"]),
                "interview_type": interview["interview_type"],
                "target_role": interview["target_role"],
                "difficulty": interview["difficulty"],
                "total_questions": interview["total_questions"],
                "current_question_index": interview.get(
                    "current_question_index", 0
                ),
                "status": interview["status"],
                "questions": questions,
            },
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

@router.post("/{interview_id}/answers")
def submit_answer(
    interview_id: str,
    request: InterviewAnswerSubmit,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = submit_interview_answer(
            interview_id=interview_id,
            firebase_uid=firebase_uid,
            question_number=request.question_number,
            answer=request.answer,
        )

        return {
            "success": True,
            "message": result["message"],
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

@router.get("/{interview_id}/results")
def get_interview_result_details(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
):
    firebase_uid = current_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    try:
        result = get_interview_results(
            interview_id=interview_id,
            firebase_uid=firebase_uid,
        )

        return {
            "success": True,
            "message": "Interview results retrieved successfully.",
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
