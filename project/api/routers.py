from fastapi import APIRouter

router_users = APIRouter(prefix="/users", tags=["Пользователи"])
router_pyments_account = APIRouter(
    prefix="/payments_account", tags=["Счета и платежи"]
)
router_token = APIRouter(prefix="/token", tags={"Токены"})
router_webhook = APIRouter(prefix="/webhook")
