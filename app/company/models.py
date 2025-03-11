from sqlalchemy import Column, Integer, String, DateTime, func, Index, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

from pydantic import BaseModel, Field, root_validator
from datetime import datetime, timedelta, timezone
import enum


class EnumYn(str, enum.Enum):
    N = "N"
    Y = "Y"

# --------------------------------------------------------------------------------
# 테이블
# --------------------------------------------------------------------------------
class Company(Base):
    __tablename__ = "company"

    company_id = Column(Integer, primary_key=True, autoincrement=True, comment="회사아이디")
    registration_datetime = Column(DateTime, nullable=False, server_default=func.now(), comment="등록일시")


class CompanyInfo(Base):
    __tablename__ = "company_info"

    company_id = Column(Integer, primary_key=True, comment="회사아이디")
    language_type = Column(String(10), primary_key=True, comment="언어유형")
    company_name = Column(String(200), nullable=False, comment="회사이름")
    registration_datetime = Column(DateTime, nullable=False, server_default=func.now(), comment="등록일시")


class CommonTag(Base):
    __tablename__ = "common_tag"

    tag_id = Column(Integer, primary_key=True, autoincrement=True, comment="태그아이디")
    tag_group_id = Column(Integer, nullable=False, comment="태그그룹아이디")
    language_type = Column(String(10), nullable=False, comment="언어유형")
    tag_name = Column(String(200), nullable=False, comment="태그이름")
    registration_datetime = Column(DateTime, nullable=False, server_default=func.now(), comment="등록일시")

    # language_type과 tag_name에 대해 유니크 인덱스를 생성
    __table_args__ = (
        Index('ix_tag_name_language_type_unique', 'language_type', 'tag_name', unique=True),
    )


class CompanyTagMapping(Base):
    __tablename__ = "company_tag_mapping"

    company_tag_mapping_id = Column(Integer, primary_key=True, autoincrement=True, comment="회사태그맵핑아이디")
    company_id = Column(Integer, nullable=False, comment="회사아이디")
    tag_id = Column(Integer, nullable=False, comment="태그아이디")
    registration_datetime = Column(DateTime, nullable=False, server_default=func.now(), comment="등록일시")
    delete_yn = Column(Enum(EnumYn), nullable=False, server_default=EnumYn.N, comment="삭제여부")
    delete_datetime = Column(DateTime, nullable=True, comment="삭제일시")