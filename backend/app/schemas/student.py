from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class StudentLogin(BaseModel):
    phone: str
    password: str


class StudentResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    is_active: bool

    class Config:
        from_attributes = True
