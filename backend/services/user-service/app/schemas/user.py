from pydantic import BaseModel, Field


class UserProfileCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    target_role: str | None = Field(default=None, max_length=100)
    skills: list[str] = Field(default_factory=list)


class UserProfileResponse(BaseModel):
    id: str
    firebase_uid: str
    email: str
    name: str
    target_role: str | None = None
    skills: list[str] = Field(default_factory=list)