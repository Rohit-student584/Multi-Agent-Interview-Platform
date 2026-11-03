from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.prompts.feedback_prompt import FEEDBACK_EVALUATION_PROMPT
from app.schemas.feedback import FeedbackResponse


# Create feedback evaluation prompt
feedback_prompt = ChatPromptTemplate.from_template(
    FEEDBACK_EVALUATION_PROMPT
)

# Configure Gemini for structured output

# Configure Groq with strict structured output
structured_llm = llm.with_structured_output(
    FeedbackResponse,
    method="json_schema",
    strict=True,
)


# Create feedback evaluation chain
feedback_chain = feedback_prompt | structured_llm


def evaluate_interview_answer(
    interview_type: str,
    target_role: str,
    difficulty: str,
    question: str,
    topic: str,
    expected_answer: str,
    evaluation_criteria: list[str],
    candidate_answer: str,
) -> dict:
    """Evaluate a candidate's interview answer using Gemini."""

    if not candidate_answer or not candidate_answer.strip():
        raise ValueError("Candidate answer cannot be empty.")

    if not question.strip():
        raise ValueError("Interview question cannot be empty.")

    if not expected_answer.strip():
        raise ValueError("Expected answer cannot be empty.")

    criteria_text = "\n".join(
        f"- {criterion}"
        for criterion in evaluation_criteria
    )

    result = feedback_chain.invoke({
        "interview_type": interview_type,
        "target_role": target_role,
        "difficulty": difficulty,
        "question": question,
        "topic": topic,
        "expected_answer": expected_answer,
        "evaluation_criteria": criteria_text,
        "candidate_answer": candidate_answer,
    })

    return result.model_dump()