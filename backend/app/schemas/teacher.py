from pydantic import BaseModel


class TeacherCreate(BaseModel):
    full_name: str
    phone: str
    password: str
    subject: str


class TeacherLogin(BaseModel):
    phone: str
    password: str


class TeacherResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    subject: str
    is_active: bool

    class Config:
        from_attributes = True
