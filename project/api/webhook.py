import hashlib
import os

from api.exceptions import ExceptionSaveDataBase, NotValidSignature
from api.models_for_api.pydantic_models import WebHookRequest
from api.routers import router_webhook
from api.utils import check_unique_transaction
from database import get_db
from dotenv import load_dotenv
from fastapi import Depends
from models.models import Account, Payment
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()


@router_webhook.post("/")
async def webhook(
    form_data: WebHookRequest,
    session: AsyncSession = Depends(get_db)
) -> None:

    str_for_hash = (
        f"{form_data.account_id}"
        f"{form_data.amount}"
        f"{form_data.transaction_id}"
        f"{form_data.user_id}"
        f"{os.getenv('SECRET_KEY_FOR_HASH')}"
    ).encode("utf-8")

    hash_str = hashlib.sha256(str_for_hash).hexdigest()

    if hash_str != form_data.signature:
        raise NotValidSignature()

    await check_unique_transaction(
        session=session,
        transaction_id=form_data.transaction_id
    )

    query = await session.execute(
        select(Account).filter_by(
            number=form_data.account_id,
            user_id=form_data.user_id
        )
    )
    payment = Payment(
        transaction=form_data.transaction_id,
        amount=form_data.amount
    )
    if not (account := query.scalar()):
        new_account = Account(
            user_id=form_data.user_id,
            number=form_data.account_id,
            balance=form_data.amount
        )
        session.add(new_account)
        payment.account_id = new_account.id
    else:
        account.balance += form_data.amount
        payment.account_id = account.id

    session.add(payment)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise ExceptionSaveDataBase(error=e)
