from datetime import datetime

import pydantic as pd


class PageUrlDomainCreateSerializer(pd.BaseModel):
    name: str


class PageUrlDomainReadSerializer(pd.BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    name: str

    class Config:
        orm_mode = True


class BaseCheckResponseModel(pd.BaseModel):
    present: list[str]
    not_present: list[str]
