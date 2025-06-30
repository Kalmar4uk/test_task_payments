from fastapi import HTTPException


class NotValidToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Невалидный токен"
        )


class NotValidEmailOrPassword(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Некорректный Email и/или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotAuth(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Необходимо авторизоваться",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotRights(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Недостаточно прав"
        )


class NotValidPassowod(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Введен некорректный текущий пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFound(HTTPException):
    def __init__(self, user_id: int | None = None, email: str | None = None):
        if email:
            super().__init__(
                status_code=404,
                detail=f"Сотрудник с email {email} не найден"
            )
        else:
            super().__init__(
                status_code=404,
                detail=f"Сотрудник с id {user_id} не найден"
            )


class UniqueEmailEmployee(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Email уже используется"
        )


class ExceptionSaveDataBase(HTTPException):
    def __init__(self, error):
        super().__init__(
            status_code=500,
            detail=f"Произошла ошибка при сохранении записи в БД: {error}"
        )


class NotValidSignature(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Подпись объекта некорректа"
        )


class UniqueTransactionId(HTTPException):
    def __init__(self, transaction):
        super().__init__(
            status_code=400,
            detail=f"Начисления по транзации {transaction} уже произведены"
        )
