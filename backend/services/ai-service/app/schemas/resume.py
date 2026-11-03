from pydantic import BaseModel, Field


class ResumeAnalysisResponse(BaseModel):
    estimated_ats_score: int = Field(
        ge=0,
        le=100,
        description="Estimated ATS compatibility score from 0 to 100",
    )

    overall_summary: str

    strengths: list[str]

    weaknesses: list[str]

    missing_keywords: list[str]

    improvement_suggestions: list[str]

    rewritten_summary: str

    recommended_roles: list[str]