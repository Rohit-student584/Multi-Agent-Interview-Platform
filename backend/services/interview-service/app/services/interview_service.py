from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import db


# MongoDB interview sessions collection
interviews_collection = db["interviews"]


def create_interview_session(
    firebase_uid: str,
    interview_data: dict,
) -> dict:
    """Create and save a new interview session."""

    now = datetime.now(timezone.utc)

    interview = {
        "firebase_uid": firebase_uid,
        "interview_type": interview_data["interview_type"],
        "target_role": interview_data["target_role"],
        "difficulty": interview_data["difficulty"],
        "total_questions": interview_data["total_questions"],
        "status": "created",
        "current_question_index": 0,
        "questions": [],
        "answers": [],
        "feedback": None,
        "created_at": now,
        "updated_at": now,
    }

    result = interviews_collection.insert_one(interview)

    return {
        "id": str(result.inserted_id),
        "firebase_uid": firebase_uid,
        "interview_type": interview["interview_type"],
        "target_role": interview["target_role"],
        "difficulty": interview["difficulty"],
        "total_questions": interview["total_questions"],
        "status": interview["status"],
    }

def get_user_interviews(firebase_uid: str) -> list[dict]:
    """Retrieve interview history with scores for a user."""

    documents = interviews_collection.find(
        {"firebase_uid": firebase_uid}
    ).sort("created_at", -1)

    interviews = []

    for document in documents:
        answers = document.get("answers", [])

        scores = [
            answer["feedback"]["score"]
            for answer in answers
            if isinstance(
                answer.get("feedback", {}).get("score"),
                (int, float),
            )
            and not isinstance(
                answer.get("feedback", {}).get("score"),
                bool,
            )
        ]

        average_score = (
            round(sum(scores) / len(scores), 2)
            if scores
            else None
        )

        created_at = document.get("created_at")
        completed_at = document.get("completed_at")

        interviews.append({
            "id": str(document["_id"]),
            "interview_type": document["interview_type"],
            "target_role": document["target_role"],
            "difficulty": document["difficulty"],
            "total_questions": document["total_questions"],
            "status": document["status"],
            "answered_questions": len(answers),
            "evaluated_questions": len(scores),
            "average_score": average_score,
            "percentage": (
                round((average_score / 10) * 100, 2)
                if average_score is not None
                else None
            ),
            "created_at": (
                created_at.isoformat()
                if created_at
                else None
            ),
            "completed_at": (
                completed_at.isoformat()
                if completed_at
                else None
            ),
        })

    return interviews



def get_interview_session(
    interview_id: str,
    firebase_uid: str,
) -> dict:
    """Retrieve an interview session belonging to a user."""

    if not ObjectId.is_valid(interview_id):
        raise ValueError("Invalid interview ID.")

    interview = interviews_collection.find_one({
        "_id": ObjectId(interview_id),
        "firebase_uid": firebase_uid,
    })

    if interview is None:
        raise LookupError("Interview session not found.")

    return interview


def save_interview_questions(
    interview_id: str,
    firebase_uid: str,
    questions: list[dict],
) -> dict:
    """Save AI-generated questions into an interview session."""

    interview = get_interview_session(
        interview_id=interview_id,
        firebase_uid=firebase_uid,
    )

    if len(questions) != interview["total_questions"]:
        raise ValueError(
            "Generated question count does not match the session."
        )

    now = datetime.now(timezone.utc)

    interviews_collection.update_one(
        {
            "_id": interview["_id"],
            "firebase_uid": firebase_uid,
        },
        {
            "$set": {
                "questions": questions,
                "current_question_index": 0,
                "status": "in_progress",
                "updated_at": now,
            }
        },
    )

    return {
        "id": str(interview["_id"]),
        "interview_type": interview["interview_type"],
        "target_role": interview["target_role"],
        "difficulty": interview["difficulty"],
        "total_questions": interview["total_questions"],
        "status": "in_progress",
        "questions": questions,
    }

def submit_interview_answer(
    interview_id: str,
    firebase_uid: str,
    question_number: int,
    answer: str,
) -> dict:
    """Save a candidate's answer and advance the interview session."""

    interview = get_interview_session(
        interview_id=interview_id,
        firebase_uid=firebase_uid,
    )

    if interview.get("status") != "in_progress":
        raise ValueError("This interview is not accepting answers.")

    questions = interview.get("questions", [])
    total_questions = interview.get("total_questions", 0)
    current_index = interview.get("current_question_index", 0)

    if not questions or current_index >= total_questions:
        raise ValueError("No pending interview questions.")

    expected_question_number = current_index + 1

    if question_number != expected_question_number:
        raise ValueError(
            f"Please answer question {expected_question_number} first."
        )

    if question_number > len(questions):
        raise ValueError("Question not found.")

    if not answer or not answer.strip():
        raise ValueError("Answer cannot be empty.")

    now = datetime.now(timezone.utc)

    answer_entry = {
        "question_number": question_number,
        "answer": answer.strip(),
        "submitted_at": now,
    }

    next_index = current_index + 1
    is_completed = next_index >= total_questions

    update_fields = {
        "current_question_index": next_index,
        "updated_at": now,
    }

    if is_completed:
        update_fields["status"] = "completed"
        update_fields["completed_at"] = now

    result = interviews_collection.update_one(
        {
            "_id": interview["_id"],
            "firebase_uid": firebase_uid,
            "current_question_index": current_index,
            "status": "in_progress",
        },
        {
            "$push": {"answers": answer_entry},
            "$set": update_fields,
        },
    )

    if result.modified_count != 1:
        raise ValueError(
            "Interview session changed. Please refresh and try again."
        )

    return {
        "interview_id": str(interview["_id"]),
        "question_number": question_number,
        "answers_submitted": next_index,
        "total_questions": total_questions,
        "status": "completed" if is_completed else "in_progress",
        "message": (
            "Interview completed successfully."
            if is_completed
            else "Answer submitted successfully."
        ),
    }

def get_interview_results(
    interview_id: str,
    firebase_uid: str,
) -> dict:
    """Calculate and retrieve overall interview performance."""

    interview = get_interview_session(
        interview_id=interview_id,
        firebase_uid=firebase_uid,
    )

    if interview.get("status") != "completed":
        raise ValueError("Interview is not completed yet.")

    questions = interview.get("questions", [])
    answers = interview.get("answers", [])

    question_map = {
        question["question_number"]: question
        for question in questions
    }

    question_results = []
    scores = []

    all_strengths = []
    all_missing_points = []
    all_suggestions = []

    for answer in answers:
        question_number = answer["question_number"]
        question = question_map.get(question_number, {})
        feedback = answer.get("feedback")

        result = {
            "question_number": question_number,
            "question": question.get("question", ""),
            "candidate_answer": answer.get("answer", ""),
            "feedback_available": feedback is not None,
        }

        if feedback:
            score = feedback.get("score")

            if isinstance(score, (int, float)) and not isinstance(score, bool):
                scores.append(score)

            result.update({
                "score": score,
                "answer_quality": feedback.get("answer_quality"),
                "feedback": feedback.get("feedback"),
                "strengths": feedback.get("strengths", []),
                "missing_points": feedback.get("missing_points", []),
                "improvement_suggestions": feedback.get(
                    "improvement_suggestions", []
                ),
            })

            all_strengths.extend(feedback.get("strengths", []))
            all_missing_points.extend(
                feedback.get("missing_points", [])
            )
            all_suggestions.extend(
                feedback.get("improvement_suggestions", [])
            )

        question_results.append(result)

    evaluated_count = len(scores)
    total_questions = interview.get("total_questions", 0)

    average_score = (
        round(sum(scores) / evaluated_count, 2)
        if evaluated_count
        else None
    )

    percentage = (
        round((average_score / 10) * 100, 2)
        if average_score is not None
        else None
    )

    return {
        "interview_id": str(interview["_id"]),
        "interview_type": interview["interview_type"],
        "target_role": interview["target_role"],
        "difficulty": interview["difficulty"],
        "total_questions": total_questions,
        "answered_questions": len(answers),
        "evaluated_questions": evaluated_count,
        "pending_feedback": total_questions - evaluated_count,
        "average_score": average_score,
        "percentage": percentage,
        "max_score": 10,
        "evaluation_status": (
            "completed"
            if evaluated_count == total_questions
            else "pending"
        ),
        "question_results": question_results,
        "overall_strengths": list(dict.fromkeys(all_strengths)),
        "overall_missing_points": list(
            dict.fromkeys(all_missing_points)
        ),
        "overall_improvement_suggestions": list(
            dict.fromkeys(all_suggestions)
        ),
    }
