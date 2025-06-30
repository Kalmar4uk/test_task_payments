from api.auth import get_current_user
from api.exceptions import ExceptionSaveDataBase
from api.models_for_api.pydantic_models import (AccountResponce, UserCreate,
                                                UserResponse, UserUpdate,
                                                UserWithPaymentsResponse)
from api.routers import router_users
from api.utils import check_unique_email
from database import get_db
from fastapi import Depends, Security
from models.models import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


@router_users.get("/me", response_model=UserResponse)
async def current_user(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=(
            f"{current_user.last_name} "
            f"{current_user.first_name} "
            f"{current_user.middle_name if current_user.middle_name else ''}"
        )
    )


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

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=(
            f"{user.last_name} "
            f"{user.first_name} "
            f"{user.middle_name if user.middle_name else ''}"
        )
    )


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

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=(
            f"{user.last_name} "
            f"{user.first_name} "
            f"{user.middle_name if user.middle_name else ''}"
        )
    )


@router_users.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: User = Security(get_current_user, scopes=["admin"]),
    session: AsyncSession = Depends(get_db)
) -> None:

    user = await session.get(User, user_id)
    await session.delete(user)
    await session.commit()


@router_users.get("/all-users", response_model=list[UserWithPaymentsResponse])
async def get_list_users(
    current_user: User = Security(get_current_user, scopes=["admin"]),
    session: AsyncSession = Depends(get_db)
):
    query = select(User).where(
        User.id != current_user.id
    ).options(
        selectinload(User.accounts)
    )
    result = await session.execute(query)
    return [
        UserWithPaymentsResponse(
            id=user.id,
            email=user.email,
            full_name=(
                f"{user.last_name} "
                f"{user.first_name} "
                f"{user.middle_name if user.middle_name else ''}"
            ),
            accounts=[
                AccountResponce(
                    id=account.id,
                    balance=account.balance
                ) for account in user.accounts
            ]
        ) for user in result.scalars()
    ]
