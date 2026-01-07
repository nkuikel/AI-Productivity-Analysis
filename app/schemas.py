from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    github_username: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    github_username: str | None = None

    class Config:
        from_attributes = True
