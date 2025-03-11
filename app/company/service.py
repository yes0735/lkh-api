from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas
from .models import Company, CompanyInfo, CommonTag, CompanyTagMapping
import csv

def company_name_autocomplete(
    query: str,
    x_wanted_language: str,
    db: Session
):
    try:
        company_info_list = crud.select_company_info_company_name_like_list(db=db, company_name=query, language_type=x_wanted_language)

    except Exception as e:
        raise e

    return company_info_list


def company_search(
    company_name: str,
    x_wanted_language: str,
    db: Session
):
    try:
        db_company_info = crud.select_company_info_company_name(db=db, company_name=company_name)
        
        if db_company_info is None:
            raise HTTPException(status_code=404) 

        company_info = crud.select_company_info_company_id(db=db, company_id=db_company_info.company_id, x_wanted_language=x_wanted_language)
        tag_list = crud.select_common_tag_list(db=db, company_id=db_company_info.company_id, x_wanted_language=x_wanted_language)

        tags = [tag.tag_name for tag in tag_list]

    except Exception as e:
        raise e

    return {
        "company_name": company_info.company_name,
        "tags": tags,
    }


def new_company(
    request_body: schemas.RequestCompanies,
    x_wanted_language: str,
    db: Session
):
    try:
        db.begin()

        # company_id = company insert 
        db_company = crud.insert_company(db=db)

        for language_type, company_name in request_body.company_name.items(): 
            # company_info insert 
            insert_company_info_params = {
                'company_id': db_company.company_id,
                'language_type': language_type,
                'company_name': company_name
            }
            db_company_info = crud.insert_company_info(db=db, insert_params=insert_company_info_params)

        for tags in request_body.tags:

            tag_group_id = None

            for language_type, tag_name in tags.tag_name.items():
                # tag_id = common_tag 중복 태그 있는지 조회 
                db_common_tag = crud.select_common_tag_tag_name_language_type(db=db, tag_name=tag_name, language_type=language_type)

                if db_common_tag:
                    tag_group_id = db_common_tag.tag_group_id

                if db_common_tag is None:
                    if tag_group_id is None:
                        # 그룹 마지막 번호 조회
                        tag_group_id = crud.select_common_tag_max_tag_group_id(db=db)

                    # common_tag insert 
                    db_common_tag = crud.insert_common_tag(db=db, tag_group_id=tag_group_id, tag_name=tag_name, language_type=language_type)

                # company_tag_mapping insert 
                db_company_tag_mapping = crud.insert_company_tag_mapping(db=db, company_id=db_company.company_id, tag_id=db_common_tag.tag_id)


        # company = x_wanted_language 기준으로 회사 데이터 조회
        company_info = crud.select_company_info_company_id(db=db, company_id=db_company.company_id, x_wanted_language=x_wanted_language)
        tag_list = crud.select_common_tag_list(db=db, company_id=db_company.company_id, x_wanted_language=x_wanted_language)
        tags = [tag.tag_name for tag in tag_list]

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    
    return {
        "company_name": company_info.company_name,
        "tags": tags,
    }


def search_tag_name(
    query: str,
    x_wanted_language: str,
    db: Session
):
    try:
        company_info_list = crud.select_common_tag_tag_name_language_type_list(db=db, tag_name=query, language_type=x_wanted_language)

    except Exception as e:
        raise e

    return company_info_list


def new_tag(
    company_name: str,
    request_body: List[schemas.TagName],
    x_wanted_language: str,
    db: Session
):
    try:
        db.begin()
        
        db_company_info = crud.select_company_info_company_name(db=db, company_name=company_name)

        for tags in request_body:

            tag_group_id = None

            for language_type, tag_name in tags.tag_name.items():
                # tag_id = common_tag 중복 태그 있는지 조회 
                db_common_tag = crud.select_common_tag_tag_name_language_type(db=db, tag_name=tag_name, language_type=language_type)

                if db_common_tag:
                    tag_group_id = db_common_tag.tag_group_id

                if db_common_tag is None:
                    if tag_group_id is None:
                        # 그룹 마지막 번호 조회
                        tag_group_id = crud.select_common_tag_max_tag_group_id(db=db)

                    # common_tag insert 
                    db_common_tag = crud.insert_common_tag(db=db, tag_group_id=tag_group_id, tag_name=tag_name, language_type=language_type)

                # company_tag_mapping insert 
                db_company_tag_mapping = crud.insert_company_tag_mapping(db=db, company_id=db_company_info.company_id, tag_id=db_common_tag.tag_id)


        # company = x_wanted_language 기준으로 회사 데이터 조회
        company_info = crud.select_company_info_company_id(db=db, company_id=db_company_info.company_id, x_wanted_language=x_wanted_language)
        tag_list = crud.select_common_tag_list(db=db, company_id=db_company_info.company_id, x_wanted_language=x_wanted_language)
        tags = sorted([tag.tag_name for tag in tag_list], key=lambda x: int(x.split("_")[1]))

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    
    return {
        "company_name": company_info.company_name,
        "tags": tags,
    }


def delete_tag(
    company_name: str,
    tag_name: str,
    x_wanted_language: str,
    db: Session
):
    """
    회사 태그 삭제시 동일한 language type 태그도 (논리)삭제됩니다.
    """
    try:
        db.begin()
        
        db_company_info = crud.select_company_info_company_name(db=db, company_name=company_name)
        db_tag_info = crud.select_common_tag_tag_name(db=db, tag_name=tag_name)
        db_company_tag_mapping_list = crud.select_company_tag_mapping_list(db=db, company_id=db_company_info.company_id, tag_group_id=db_tag_info.tag_group_id)

        for db_company_tag_mapping in db_company_tag_mapping_list:
            db_company_tag_mapping.delete_yn = 'Y'

        # company = x_wanted_language 기준으로 회사 데이터 조회
        company_info = crud.select_company_info_company_id(db=db, company_id=db_company_info.company_id, x_wanted_language=x_wanted_language)
        tag_list = crud.select_common_tag_list(db=db, company_id=db_company_info.company_id, x_wanted_language=x_wanted_language)
        tags = sorted([tag.tag_name for tag in tag_list], key=lambda x: int(x.split("_")[1]))

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    
    return {
        "company_name": company_info.company_name,
        "tags": tags,
    }


def import_csv(
    db: Session
):
    try:
        file_path = "data/company_tag_sample.csv"
        tag_id_counter = 1  # 그룹 ID 시작값

        with open(file_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                tag_groups = {}  # { 그룹 ID: [태그_ko, 태그_en, 태그_ja] }
                # company insert 
                company = db.query(Company).filter_by(company_id=row.get("company_ko")).first()
                if not company:
                    company = crud.insert_company(db=db)
                company_id = company.company_id

                # company_info insert 
                for lang, column in [("ko", "company_ko"), ("en", "company_en"), ("ja", "company_ja")]:
                    if row.get(column):
                        insert_company_info_params = {
                            'company_id': company_id,
                            'language_type': lang,
                            'company_name': row[column]
                        }
                        db_company_info = crud.insert_company_info(db=db, insert_params=insert_company_info_params)


                # 태그 데이터를 ko, en, ja 별로 리스트로 저장
                tag_ko_list = row["tag_ko"].split("|") if row.get("tag_ko") else []
                tag_en_list = row["tag_en"].split("|") if row.get("tag_en") else []
                tag_ja_list = row["tag_ja"].split("|") if row.get("tag_ja") else []

                for ko, en, ja in zip(tag_ko_list, tag_en_list, tag_ja_list):
                    tag_groups[tag_id_counter] = [{'ko': ko}, {'en': en}, {'ja': ja}]
                    tag_id_counter += 1  # 다음 그룹 id 증가


                for tag_group_id, tag_group_list in tag_groups.items():
                    for tag_group in tag_group_list:
                        for lang, tag_name in tag_group.items():
                            tag = crud.select_common_tag_tag_name_language_type(db=db, tag_name=tag_name, language_type=lang)
                            if not tag:
                                tag = crud.insert_common_tag(db=db, tag_group_id=tag_group_id, tag_name=tag_name, language_type=lang)

                            db_company_tag_mapping = crud.insert_company_tag_mapping(db=db, company_id=company_id, tag_id=tag.tag_id)

        # 최종 DB 커밋
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    
    return {}