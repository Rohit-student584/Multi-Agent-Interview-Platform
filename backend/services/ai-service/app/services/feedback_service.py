
from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import db
from app.agents.feedback_agent import evaluate_interview_answer


# MongoDB interview sessions collection
interviews_collection = db["interviews"]


def evaluate_and_save_answer_feedback(
    interview_id: str,
    firebase_uid: str,
    question_number: int,
) -> dict:
    """Evaluate a submitted answer and save its AI feedback."""

    if not ObjectId.is_valid(interview_id):
        raise ValueError("Invalid interview ID.")

    # Retrieve the user's interview session
    interview = interviews_collection.find_one({
        "_id": ObjectId(interview_id),
        "firebase_uid": firebase_uid,
    })

    if interview is None:
        raise LookupError("Interview session not found.")

    questions = interview.get("questions", [])
    answers = interview.get("answers", [])

    # Find the requested question
    question_data = next(
        (
            item for item in questions
            if item["question_number"] == question_number
        ),
        None,
    )

    if question_data is None:
        raise LookupError("Interview question not found.")

    # Find the candidate's submitted answer
    answer_data = next(
        (
            item for item in answers
            if item["question_number"] == question_number
        ),
        None,
    )

    if answer_data is None:
        raise LookupError("Candidate answer has not been submitted.")

    # Return previously saved feedback without calling Gemini again
    existing_feedback = answer_data.get("feedback")

    if existing_feedback:
        return {
            "interview_id": interview_id,
            "question_number": question_number,
            "question": question_data["question"],
            "candidate_answer": answer_data["answer"],
            "feedback": existing_feedback,
            "message": "Previously saved feedback retrieved successfully.",
            "expected_answer": question_data["expected_answer"],
        }

    expected_answer = question_data.get("expected_answer")

    if not expected_answer:
        raise ValueError("Expected answer is unavailable.")

    # Evaluate the candidate's actual submitted answer
    feedback = evaluate_interview_answer(
        interview_type=interview["interview_type"],
        target_role=interview["target_role"],
        difficulty=interview["difficulty"],
        question=question_data["question"],
        topic=question_data["topic"],
        expected_answer=expected_answer,
        evaluation_criteria=question_data["evaluation_criteria"],
        candidate_answer=answer_data["answer"],
    )

    now = datetime.now(timezone.utc)

    # Save feedback inside the corresponding answer
    result = interviews_collection.update_one(
        {
            "_id": ObjectId(interview_id),
            "firebase_uid": firebase_uid,
            "answers.question_number": question_number,
        },
        {
            "$set": {
                "answers.$.feedback": feedback,
                "answers.$.feedback_generated_at": now,
                "updated_at": now,
            }
        },
    )

    if result.modified_count != 1:
        raise RuntimeError("Failed to save interview feedback.")

    return {
        "interview_id": interview_id,
        "question_number": question_number,
        "question": question_data["question"],
        "candidate_answer": answer_data["answer"],
        "feedback": feedback,
        "feedback_generated_at": now.isoformat(),
        "expected_answer": question_data["expected_answer"],
    }
