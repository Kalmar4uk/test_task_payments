import os

from api import payments_account, tokens, users, webhook
from api.routers import (router_pyments_account, router_token, router_users,
                         router_webhook)
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()


# FastApi init
app = FastAPI(root_path="/api")

# FastApi include routers
app.include_router(router_token)
app.include_router(router_users)
app.include_router(router_pyments_account)
app.include_router(router_webhook)

# JWT parameters
SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1500
REFRESH_TOKEN_EXPIRE_DAYS = 7
