from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from app.core.security import create_access_token, verify_token
from jose import JWTError, jwt


SECRET_KEY = "CHANGE_THIS_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        student_id = payload.get("sub")

        if student_id is None:
            return None

        return int(student_id)

    except (JWTError, ValueError, TypeError):
        return None
@router.get("/me", response_model=StudentResponse)
def get_my_profile(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token kerak"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Bearer token noto'g'ri"
        )

    token = authorization.replace("Bearer ", "", 1)
    student_id = verify_token(token)

    if not student_id:
        raise HTTPException(
            status_code=401,
            detail="Token noto'g'ri yoki muddati tugagan"
        )

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="O'quvchi topilmadi"
        )

    return student
