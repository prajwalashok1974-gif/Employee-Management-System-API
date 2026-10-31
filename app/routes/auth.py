from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    employee_id: int | None = None


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: RegisterRequest, db: Session = Depends(get_db)):
    # Public registration must never allow a caller to grant themselves HR/admin.
    user = User(
        name=user_data.name,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
        role="employee",
        is_active=True,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email is already registered")
    return user


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2's standard form field is named username; this API expects the email there.
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdigit():
            raise credentials_exception
        user_id = int(subject)
    except (InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_admin_or_hr(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {"admin", "hr"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator or HR access required",
        )
    return current_user


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
