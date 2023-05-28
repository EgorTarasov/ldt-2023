from datetime import timedelta, datetime

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status
from fastapi.param_functions import Form

from pydantic.dataclasses import dataclass

from sqlalchemy.orm import Session

from jose import JWTError, jwt
from passlib.context import CryptContext


from app.data import models, crud, schemas
from app.utils.logging import log

from app.utils.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password


def get_hashed_user(user: schemas.UserCreate) -> schemas.UserCreateHashed:
    """Хеширование пароля пользователя"""
    hashed_password = get_password_hash(user.password)
    return schemas.UserCreateHashed(**user.dict(), hashed_password=hashed_password)


def authenticate_user(db: Session, user_data: schemas.UserLogin) -> models.User:
    """Авторизация пользователя"""

    db_user = crud.get_user_by_email(db, user_data.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return db_user


def create_access_token(
    data: dict[str, str | datetime], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, str | datetime]) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=30)})
    to_encode.update({"type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@dataclass
class AdditionalLoginFormData:
    stay_loggedin: bool = Form(None)


async def get_current_user(db: Session, cookie_token: str) -> models.User:
    """ "Получение текущего пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials {e}",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            str(cookie_token), settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")  # type: ignore
        if email is None:
            log.debug(f"email is None")
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError as e:
        log.debug(f"JWTError: {e}")
        raise credentials_exception
    if not token_data.email:
        log.debug(f"token_data.email is None")
        raise credentials_exception
    user = crud.get_user_by_email(db, token_data.email)
    if user is None:
        log.debug(f"User no found")
        raise credentials_exception
    return user
