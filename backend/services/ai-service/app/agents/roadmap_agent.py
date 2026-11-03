
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.prompts.roadmap_prompt import ROADMAP_GENERATION_PROMPT
from app.schemas.roadmap import RoadmapResponse


# Create roadmap generation prompt
roadmap_prompt = ChatPromptTemplate.from_template(
    ROADMAP_GENERATION_PROMPT
)


# Configure Groq for structured output
structured_llm = llm.with_structured_output(
    RoadmapResponse,
    method="json_schema",
    strict=True,
)


# Create roadmap generation chain
roadmap_chain = roadmap_prompt | structured_llm


def generate_career_roadmap(
    target_role: str,
    current_skills: list[str],
    experience_level: str,
    duration_weeks: int,
    daily_study_hours: float,
) -> dict:
    """Generate a personalized career roadmap using Groq."""

    if not target_role or not target_role.strip():
        raise ValueError("Target job role cannot be empty.")

    if duration_weeks < 1:
        raise ValueError("Roadmap duration must be at least one week.")

    if daily_study_hours <= 0:
        raise ValueError("Daily study hours must be greater than zero.")

    skills_text = (
        ", ".join(current_skills)
        if current_skills
        else "No existing skills provided"
    )

    result = roadmap_chain.invoke({
        "target_role": target_role,
        "current_skills": skills_text,
        "experience_level": experience_level,
        "duration_weeks": duration_weeks,
        "daily_study_hours": daily_study_hours,
    })

    if len(result.weekly_plan) != duration_weeks:
        raise ValueError(
            "Generated roadmap does not match the requested duration."
        )

    return result.model_dump()
