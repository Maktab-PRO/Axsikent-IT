from pydantic import BaseModel


class AdminLogin(BaseModel):
    phone: str
    password: str


class AdminResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
