from api.auth import get_current_user
from api.exceptions import ExceptionSaveDataBase
from api.models_for_api.pydantic_models import (UserCreate, UserResponse,
                                                UserUpdate)
from api.routers import router_users
from api.utils import check_unique_email
from database import get_db
from fastapi import Depends, Security
from models.models import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@router_users.get("/me", response_model=UserResponse)
async def current_user(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=f"{current_user.last_name} {current_user.first_name}"
    )
    if current_user.middle_name:
        user_response.full_name += f" {current_user.middle_name}"
        return user_response
    return user_response


@router_users.post("/", response_model=UserResponse)
async def create_user(
    form_data: UserCreate,
    current_user: User = Security(get_current_user, scopes=["admin"]),
    session: AsyncSession = Depends(get_db)
) -> UserResponse:

    await check_unique_email(session=session, email=form_data.email)

    user = User(**form_data.model_dump())

    session.add(user)
    password = user.password
    await user.set_password(password)

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise ExceptionSaveDataBase(error=e)

    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=f"{user.last_name} {user.first_name}"
    )
    if user.middle_name:
        user_response.full_name += f" {user.middle_name}"
        return user_response
    return user_response


@router_users.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    form_data: UserUpdate,
    current_user: User = Security(get_current_user, scopes=["admin"]),
    session: AsyncSession = Depends(get_db)
) -> UserResponse:

    user = await session.get(User, user_id)

    if user.email != form_data.email:
        await check_unique_email(session=session, email=form_data.email)

    user.email = form_data.email
    user.first_name = form_data.first_name
    user.last_name = form_data.last_name
    user.middle_name = form_data.middle_name
    user.is_admin = form_data.is_admin

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise ExceptionSaveDataBase(error=e)

    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=f"{user.last_name} {user.first_name}"
    )
    if user.middle_name:
        user_response.full_name += f" {user.middle_name}"
        return user_response
    return user_response


@router_users.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: User = Security(get_current_user, scopes=["admin"]),
    session: AsyncSession = Depends(get_db)
) -> None:

    user = await session.get(User, user_id)
    await session.delete(user)
    await session.commit()
