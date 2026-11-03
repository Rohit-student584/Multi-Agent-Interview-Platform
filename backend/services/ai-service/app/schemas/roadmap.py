
from pydantic import BaseModel, Field
from typing import Literal

class RoadmapGenerateRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=100)
    current_skills: list[str] = Field(default_factory=list)
    experience_level: Literal[
        "Beginner",
        "Intermediate",
        "Advanced",
    ] = "Beginner"
    duration_weeks: int = Field(ge=1, le=52)
    daily_study_hours: float = Field(gt=0, le=16)

class WeeklyRoadmap(BaseModel):
    week_number: int = Field(ge=1)
    focus: str
    topics: list[str]
    practical_tasks: list[str]
    project_or_assignment: str
    expected_learning_outcome: str


class RecommendedProject(BaseModel):
    title: str
    description: str
    skills_covered: list[str]


class RoadmapMilestone(BaseModel):
    milestone: str
    expected_week: int = Field(ge=1)
    completion_criteria: str


class RoadmapResponse(BaseModel):
    roadmap_title: str
    target_role: str
    duration_weeks: int = Field(ge=1)
    summary: str
    skills_to_learn: list[str]
    weekly_plan: list[WeeklyRoadmap]
    recommended_projects: list[RecommendedProject]
    milestones: list[RoadmapMilestone]
    final_goal: str

class RoadmapProgressUpdateRequest(BaseModel):
    week_number: int = Field(ge=1)
    completed: bool
