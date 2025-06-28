from passlib.context import CryptContext
from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.core import Model

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Model):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str | None] = mapped_column(String(70), nullable=True)
    accounts: Mapped[list["Account"]] = relationship(
        "Account", back_populates="user"
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    async def set_password(self, password: str):
        self.password = context.hash(password)

    async def check_password(self, password: str):
        return context.verify(password, self.password)


class Account(Model):
    __tablename__ = "accounts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="account"
    )
    balance: Mapped[float | None] = mapped_column(Float, nullable=True)


class Payment(Model):
    __tablename__ = "payments"

    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account: Mapped["Account"] = relationship(
        "Account", back_populates="payments"
    )
    transaction: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
