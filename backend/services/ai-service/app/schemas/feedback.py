from typing import Literal

from pydantic import BaseModel, Field


class FeedbackResponse(BaseModel):
    score: int = Field(
        ge=0,
        le=10,
        description="Candidate answer score from 0 to 10",
    )

    answer_quality: Literal[
        "Correct",
        "Partially Correct",
        "Incorrect",
    ]

    feedback: str

    strengths: list[str]

    missing_points: list[str]

    criteria_met: list[str]

    criteria_missed: list[str]

    improvement_suggestions: list[str]