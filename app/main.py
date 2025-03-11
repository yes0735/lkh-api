from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.company.router import router as company_router
from app.database import init_db, wait_for_db
import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup 대체
    wait_for_db()
    init_db()
    yield
    pass

def create_app() -> FastAPI:
    """ app 변수 생성 및 초기값 설정 """

    _app = FastAPI(
        title="LKH API",
        description="LKH FastAPI Swagger",
        version="1.0.0",
        lifespan=lifespan  # lifespan 적용
    )
    _app.include_router(company_router, prefix="", tags=["COMPANY"])
    return _app

app = create_app()

