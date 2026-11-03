from typing import Literal

from pydantic import BaseModel, Field


class InterviewSessionCreate(BaseModel):
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


class InterviewSessionResponse(BaseModel):
    id: str
    firebase_uid: str
    interview_type: str
    target_role: str
    difficulty: str
    total_questions: int
    status: str

class InterviewQuestionData(BaseModel):
    question_number: int = Field(ge=1)
    question: str
    topic: str
    expected_answer: str
    evaluation_criteria: list[str]
    sample_input: str | None = None
    sample_output: str | None = None


class InterviewQuestionsSaveRequest(BaseModel):
    questions: list[InterviewQuestionData] = Field(
        min_length=1,
        max_length=20,
    )

class InterviewAnswerSubmit(BaseModel):
    question_number: int = Field(ge=1, le=20)

    answer: str = Field(
        min_length=1,
        max_length=10000,
    )