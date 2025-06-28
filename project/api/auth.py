from datetime import datetime, timedelta

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.exceptions import NotAuth, NotRights, NotValidToken, UserNotFound
from database import get_db
from models.models import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "admin": "Admin permissions"
    },
    auto_error=False
)


def create_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode: dict = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.SECRET_KEY_JWT,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_access_token(data: dict) -> str:
    data_for_access: dict = data.copy()
    data_for_access.update(token_type="access_token")
    exp_access_token = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data_for_access,
        expires_delta=exp_access_token
    )

    return access_token


async def get_current_user(
        scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)
) -> User:
    """Проверка токена пользователя"""
    if not token:
        raise NotAuth()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY_JWT,
            algorithms=[settings.ALGORITHM]
        )
    except InvalidTokenError:
        raise NotValidToken()

    email: str = payload.get("sub")
    if not email:
        raise NotValidToken()
    token_scopes: str = payload.get("scopes", [])
    if scopes.scopes:
        for scope in scopes.scopes:
            if scope not in token_scopes:
                raise NotRights()

    try:
        query = await session.execute(select(User).filter_by(email=email))
        user = query.scalar()
    except Exception:
        raise UserNotFound(email=email)

    return user
