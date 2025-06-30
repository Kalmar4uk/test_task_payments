from api.auth import get_current_user
from api.models_for_api.pydantic_models import (AccountResponce,
                                                PaymentsResponce)
from api.routers import router_pyments_account
from database import get_db
from fastapi import Depends
from models.models import Payment, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@router_pyments_account.get(
        "/my-accounts",
        response_model=list[AccountResponce]
)
async def get_user_account(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> list[AccountResponce]:

    result = await current_user.awaitable_attrs.accounts
    return [
        AccountResponce(
            id=account.id,
            balance=account.balance
        ) for account in result
    ]


@router_pyments_account.get(
        "/my-payments",
        response_model=list[PaymentsResponce]
)
async def get_user_payments(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> list[PaymentsResponce]:
    accounts = await current_user.awaitable_attrs.accounts
    query = select(Payment).where(
        Payment.account_id.in_(
            [account.id for account in accounts]
        )
    )
    result = await session.execute(query)
    return [
        PaymentsResponce(
            id=payment.id,
            transaction=payment.transaction,
            amount=payment.amount
        ) for payment in result.scalars()
    ]
