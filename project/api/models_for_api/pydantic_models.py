import re

from pydantic import BaseModel, Field, field_validator

from api.utils import ValidationPasswordError, validate_password


class Base(BaseModel):
    id: int = Field(examples=[1])


class UserResponse(Base):
    email: str = Field(examples=["test@mail.ru"])
    full_name: str = Field(
        examples=["Фамилия Имя Отчетсво"],
        description="Отчества может не быть"
    )


class AccountResponce(Base):
    balance: float | None = Field(default=None, examples=[1000])


class PaymentsResponce(Base):
    transaction: str = Field(examples=["ex631sv12-dsad11-sda2124f"])
    amount: float = Field(examples=[1000])


class UserWithPaymentsResponse(UserResponse):
    accounts: list[AccountResponce]


class Token(BaseModel):
    """Модель токенов"""
    access_token: str = Field(examples=["dfsadfasfsdfsdfsd.ewqeqwe1213"])
    token_type: str = Field(examples=["Bearer"])


class UserLogin(BaseModel):
    """Модель для получения токена"""
    email: str = Field(examples=["olezha.korotky@mail.ru"])
    password: str = Field(examples=["Aotydfsabfdsjk145"])


class UserUpdate(BaseModel):
    email: str = Field(examples=["test@mail.ru"])
    first_name: str = Field(examples=["Имя"])
    last_name: str = Field(examples=["Фамилия"])
    middle_name: str | None = Field(default=None, examples=["Отчество"])
    is_admin: bool = Field(default=False, examples=[False])

    @field_validator("email")
    def check_email(cls, value: str):
        if not re.search(r"^[\w.]+@[\w]+\.+(ru|com)$", value):
            raise ValueError("Некорректный Email")
        return value

    @field_validator("middle_name")
    def check_middle_name(cls, value: str):
        if value == "":
            value = None
        return value


class UserCreate(UserUpdate):
    password: str = Field(examples=["Qwer1231"])

    @field_validator("password")
    def check_password(cls, value: str):
        try:
            validate_password(value)
        except ValidationPasswordError as e:
            raise ValueError(str(e))
        return value
