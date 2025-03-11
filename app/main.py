from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.company.router import router as company_router
from app.database import init_db, wait_for_db


# 앱 시작 시 데이터베이스 초기화
@asynccontextmanager
async def startup(app: FastAPI):
    wait_for_db()
    init_db()

def create_app() -> FastAPI(startup=startup):
    """ app 변수 생성 및 초기값 설정 """

    _app = FastAPI(
        title="LKH API",
        description="LKH FastAPI Swagger",
        version="1.0.0",
    )
    _app.include_router(company_router, prefix="", tags=["COMPANY"])
    return _app

app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)