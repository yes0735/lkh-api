from pydantic import BaseModel, Field



class TagName(BaseModel):
    tag_name: dict = Field(..., description="태그이름")


class CompanyName(BaseModel):
    company_name: str = Field(..., description="회사이름")


# --------------------------------------------------------------------------------
# request
# --------------------------------------------------------------------------------
class RequestCompanies(BaseModel):
    company_name: dict = Field(..., description="회사이름")
    tags: list[TagName] = Field(..., description="태그이름리스트")


# --------------------------------------------------------------------------------
# response
# --------------------------------------------------------------------------------
class ResponseCompany(CompanyName):
    tags: list = Field(..., description="태그이름리스트")
