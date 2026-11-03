from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.prompts.resume_prompt import RESUME_ANALYSIS_PROMPT
from app.schemas.resume import ResumeAnalysisResponse


# Create resume analysis prompt
resume_prompt = ChatPromptTemplate.from_template(
    RESUME_ANALYSIS_PROMPT
)

# Configure Gemini for structured output
structured_llm = llm.with_structured_output(
    ResumeAnalysisResponse
)

# Create Resume Analysis Chain
resume_analysis_chain = resume_prompt | structured_llm


def analyze_resume(
    resume_text: str,
    target_role: str = "Software Engineer",
) -> dict:
    """Analyze a resume using the Gemini AI model."""

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    analysis = resume_analysis_chain.invoke({
        "resume_text": resume_text,
        "target_role": target_role,
    })

    return analysis.model_dump()