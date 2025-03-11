from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.database import get_db
from . import schemas
from . import crud
from app.company import service
from datetime import datetime, timedelta
import pytz
from typing import List
from sqlalchemy import desc


# APIRouter 인스턴스 생성
router = APIRouter()


@router.get("/search", response_model=List[schemas.CompanyName])
def get_search(
    query: str,
    x_wanted_language: str = Header('ko'),
    db: Session = Depends(get_db)
):
    """ 1. 회사명 자동완성 """

    return service.company_name_autocomplete(
        query=query,
        x_wanted_language=x_wanted_language,
        db=db
    )


@router.get("/companies/{company_name}", response_model=schemas.ResponseCompany)
def get_companies(
    company_name: str,
    x_wanted_language: str = Header('ko'),
    db: Session = Depends(get_db)
):
    """ 2. 회사 이름으로 회사 검색 """

    return service.company_search(
        company_name=company_name,
        x_wanted_language=x_wanted_language,
        db=db
    )


@router.post("/companies")
def post_companies(
    request_body: schemas.RequestCompanies,
    x_wanted_language: str = Header('ko'),
    db: Session = Depends(get_db)
):
    """ 3. 새로운 회사 추가 """

    return service.new_company(
        request_body=request_body,
        x_wanted_language=x_wanted_language,
        db=db
    )


@router.get("/tags")
def get_tags(
    query: str,
    x_wanted_language: str = Header('ko'),
    db: Session = Depends(get_db)
):
    """ 4. 태그명으로 회사 검색 """

    return service.search_tag_name(
        query=query,
        x_wanted_language=x_wanted_language,
        db=db
    )
    

@router.put("/companies/{company_name}/tags")
def put_companies_tags(
    company_name: str,
    request_body: List[schemas.TagName],
    x_wanted_language: str = Header('ko'),
    db: Session = Depends(get_db)
):
    """ 5. 회사 태그 정보 추가 """

    return service.new_tag(
        company_name=company_name,
        request_body=request_body,
        x_wanted_language=x_wanted_language,
        db=db
    )


@router.delete("/companies/{company_name}/tags/{tag_name}")
def delete_companies_tag(
    company_name: str,
    tag_name: str,
    x_wanted_language: str = Header('ko'),
    db: Session = Depends(get_db)
):
    """ 6. 회사 태그 정보 삭제 """

    return service.delete_tag(
        company_name=company_name,
        tag_name=tag_name,
        x_wanted_language=x_wanted_language,
        db=db
    )

@router.post("/import-csv")
def post_import_csv(
    db: Session = Depends(get_db)
):
    """ 7. 샘플 데이터 등록 """
    return service.import_csv(
        db=db
    )