from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas

# 데이터 생성하기
def insert_company(db: Session):
    db_company = models.Company()
    db.add(db_company)  # DB에 해당 인스턴스 추가하기
    # db.commit()  # DB의 변경 사항 저장하기
    # db.refresh(db_company)  # 생성된 ID와 같은 DB의 새 데이터를 포함하도록 새로고침
    db.flush()
    return db_company


def insert_company_info(db: Session, insert_params: dict):
    db_company_info = models.CompanyInfo(
        company_id = insert_params.get('company_id'),
        language_type = insert_params.get('language_type'),
        company_name = insert_params.get('company_name')
    )
    db.add(db_company_info)  # DB에 해당 인스턴스 추가하기
    db.flush()
    return db_company_info
                

def insert_common_tag(db: Session, tag_group_id:int, tag_name: str, language_type: str):
    db_common_tag = models.CommonTag(
        tag_group_id = tag_group_id,
        tag_name = tag_name,
        language_type = language_type
    )
    db.add(db_common_tag)  # DB에 해당 인스턴스 추가하기
    db.flush()
    return db_common_tag
                

def insert_company_tag_mapping(db: Session, company_id: int, tag_id: int):
    db_company_tag_mapping = models.CompanyTagMapping(
        company_id = company_id,
        tag_id = tag_id
    )
    db.add(db_company_tag_mapping)  # DB에 해당 인스턴스 추가하기
    db.flush()
    return db_company_tag_mapping


def select_company_info_company_id(db: Session, company_id: int, x_wanted_language: str):
    return db.query(models.CompanyInfo).filter(
        models.CompanyInfo.company_id == company_id, 
        models.CompanyInfo.language_type == x_wanted_language
    ).first()


def select_common_tag_list(db: Session, company_id: int, x_wanted_language: str):
    return db.query(models.CommonTag).join(
        models.CompanyTagMapping, 
        models.CommonTag.tag_id == models.CompanyTagMapping.tag_id
    ).filter(
        models.CompanyTagMapping.company_id == company_id, 
        models.CompanyTagMapping.delete_yn == 'N',
        models.CommonTag.language_type == x_wanted_language
    ).all()


def select_common_tag_tag_name_language_type(db: Session, tag_name: str, language_type: str):
    return db.query(models.CommonTag).filter(
        models.CommonTag.tag_name == tag_name, 
        models.CommonTag.language_type == language_type
    ).first()


def select_company_info_company_name_like_list(db: Session, company_name: str, language_type: str):
    return db.query(models.CompanyInfo.company_name).filter(
        models.CompanyInfo.company_name.ilike(f"%{company_name}%"),
        models.CompanyInfo.language_type == language_type
    ).all()


def select_company_info_company_name(db: Session, company_name: str):
    return db.query(models.CompanyInfo).filter(
        models.CompanyInfo.company_name == company_name
    ).first()


def select_common_tag_tag_name_language_type_list(db: Session, tag_name: str, language_type: str):
    # 첫 번째 쿼리 (language_type 언어만 선택)
    stmt = db.query(models.CompanyInfo).join(
        models.CompanyTagMapping, models.CompanyInfo.company_id == models.CompanyTagMapping.company_id
    ).join(
        models.CommonTag, models.CompanyTagMapping.tag_id == models.CommonTag.tag_id
    ).filter(
        models.CommonTag.tag_name == tag_name,
        models.CompanyTagMapping.delete_yn == 'N',
        models.CompanyInfo.language_type == language_type
    )

    # 두 번째 쿼리 (language_type 언어가 아닌 것들 중, language_type 언어에 해당하는 매핑을 제외한 것들만 선택)
    # `NOT IN` 조건을 사용하여 `company_tag_mapping_id`가 첫 번째 쿼리에서 반환된 language_type 데이터를 제외
    stmt_non = db.query(models.CompanyInfo).join(
        models.CompanyTagMapping, models.CompanyInfo.company_id == models.CompanyTagMapping.company_id
    ).join(
        models.CommonTag, models.CompanyTagMapping.tag_id == models.CommonTag.tag_id
    ).filter(
        models.CommonTag.tag_name == tag_name,
        models.CompanyTagMapping.delete_yn == 'N',
        models.CompanyInfo.language_type != language_type
    ).filter(
        models.CompanyTagMapping.company_tag_mapping_id.notin_(
            db.query(models.CompanyTagMapping.company_tag_mapping_id)
            .join(models.CompanyInfo, models.CompanyTagMapping.company_id == models.CompanyInfo.company_id)
            .join(models.CommonTag, models.CompanyTagMapping.tag_id == models.CommonTag.tag_id)
            .filter(
                models.CommonTag.tag_name == tag_name,
                models.CompanyTagMapping.delete_yn == 'N',
                models.CompanyInfo.language_type == language_type
            )
        )
    ).group_by(models.CompanyInfo.company_id)

    # 실행 및 결과 조회
    union_stmt = stmt.union_all(stmt_non).subquery()
    result = db.query(union_stmt).order_by(union_stmt.c.company_info_company_id).all()

    # 결과를 딕셔너리로 변환
    result_dict = [
        {
            "company_id": row.company_info_company_id,
            "company_name": row.company_info_company_name
        }
        for row in result
    ]

    return result_dict


def select_common_tag_tag_name(db: Session, tag_name: str):
    return db.query(models.CommonTag).filter(
        models.CommonTag.tag_name == tag_name
    ).first()


def select_company_tag_mapping_list(db: Session, company_id: int, tag_group_id: int):
    return db.query(models.CompanyTagMapping).join(
        models.CommonTag, 
        models.CompanyTagMapping.tag_id == models.CommonTag.tag_id
    ).filter(
        models.CompanyTagMapping.company_id == company_id, 
        models.CommonTag.tag_group_id == tag_group_id,
        models.CompanyTagMapping.delete_yn == 'N'
    ).all()


def select_common_tag_max_tag_group_id(db: Session):
    max_tag_group_id = db.query(func.max(models.CommonTag.tag_group_id)).scalar()
    return max_tag_group_id