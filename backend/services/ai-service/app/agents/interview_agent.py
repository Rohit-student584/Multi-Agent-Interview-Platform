
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.prompts.interview_prompt import INTERVIEW_QUESTION_PROMPT
from app.schemas.interview import InterviewQuestionSet


# Create interview question prompt
interview_prompt = ChatPromptTemplate.from_template(
    INTERVIEW_QUESTION_PROMPT
)

# Configure Gemini for structured output
structured_llm = llm.with_structured_output(
    InterviewQuestionSet
)

# Create interview question generation chain
interview_question_chain = interview_prompt | structured_llm


def generate_interview_questions(
    interview_type: str,
    target_role: str,
    difficulty: str,
    total_questions: int = 5,
) -> dict:
    """Generate structured interview questions using Gemini."""

    allowed_types = {"HR", "Technical", "Coding"}
    allowed_difficulties = {
        "Beginner",
        "Intermediate",
        "Advanced",
    }

    if interview_type not in allowed_types:
        raise ValueError("Invalid interview type.")

    if difficulty not in allowed_difficulties:
        raise ValueError("Invalid difficulty level.")

    if not target_role.strip():
        raise ValueError("Target role cannot be empty.")

    if not 1 <= total_questions <= 20:
        raise ValueError("Total questions must be between 1 and 20.")

    result = interview_question_chain.invoke({
        "interview_type": interview_type,
        "target_role": target_role,
        "difficulty": difficulty,
        "total_questions": total_questions,
    })

    if len(result.questions) != total_questions:
        raise ValueError(
            "AI did not generate the requested number of questions."
        )

    return result.model_dump()
