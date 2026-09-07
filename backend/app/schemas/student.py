from pydantic import BaseModel


class StudentCreate(BaseModel):
    full_name: str
    phone: str
    password: str


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
