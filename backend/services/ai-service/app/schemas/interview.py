from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question_number: int = Field(ge=1)

    question: str

    topic: str

    expected_answer: str

    evaluation_criteria: list[str]

    sample_input: str | None = None

    sample_output: str | None = None


class InterviewQuestionSet(BaseModel):
    questions: list[InterviewQuestion]