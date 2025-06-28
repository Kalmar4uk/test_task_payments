from api.auth import get_access_token
from api.exceptions import NotValidEmailOrPassword, UserNotFound
from api.models_for_api.pydantic_models import Token, UserLogin
from api.routers import router_token
from database import get_db
from fastapi import Depends
from models.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@router_token.post("/login", response_model=Token)
async def login(
    from_data: UserLogin,
    session: AsyncSession = Depends(get_db)
) -> Token:
    try:
        query = await session.execute(
            select(User).filter_by(
                email=from_data.email)
            )
        user = query.scalar()
    except Exception:
        raise UserNotFound(email=from_data.email)
    if not await user.check_password(from_data.password):
        raise NotValidEmailOrPassword()

    data = {"sub": user.email}
    if user.is_admin:
        data["scopes"] = "admin"

    access_token = get_access_token(
        data=data
    )

    return Token(
        access_token=access_token,
        token_type="Bearer"
    )
