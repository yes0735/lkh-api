import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "leekh123!")
DB_HOST = os.getenv("DB_HOST", "host.docker.internal:3306")
DB_NAME = os.getenv("DB_NAME", "work")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)  # , echo=True 쿼리실행문
SessionLocal = sessionmaker(autocommit=False, bind=engine)

Base = declarative_base()


# 데이터베이스 초기화 함수
def init_db():
    Base.metadata.create_all(bind=engine)

# 데이터베이스 세션을 반환하는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()