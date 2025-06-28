from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import UniqueEmailEmployee
from models.models import User


class ValidationPasswordError(Exception):
    """Искючение валидации пароля"""
    pass


BAD_PASSWORD = [
    "Qwerty123",
    "Qwerty12345",
    "Qwerty1234"
]


def validate_password(password: str) -> None:
    """Валидация пароля"""
    if len(password) < 8:
        raise ValidationPasswordError(
            "Пароль должен состоять минимум из 8 символов"
        )
    if password.isdigit():
        raise ValidationPasswordError(
            "Пароль не должен состоять только из цифр"
        )
    if password.islower():
        raise ValidationPasswordError(
            "В пароле должна быть хотя бы одна заглавная буква"
        )
    if password.isspace():
        raise ValidationPasswordError(
            "Некорректный пароль"
        )
    if password in BAD_PASSWORD:
        raise ValidationPasswordError(
            "Введен распространенный пароль"
        )


async def check_unique_email(session: AsyncSession, email: str) -> None:
    query = await session.execute(
        select(
            exists().where(
                User.email == email
            )
        )
    )
    if query.scalar():
        raise UniqueEmailEmployee()
