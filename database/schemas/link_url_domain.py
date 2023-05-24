from datetime import datetime

import pydantic as pd


class LinkUrlDomainCreateSerializer(pd.BaseModel):
    name: str


class LinkUrlDomainReadSerializer(pd.BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    name: str

    class Config:
        orm_mode = True


class LinkUrlDomainUpdateSerializerV2(pd.BaseModel):
    is_base: bool


class LinkUrlDomainCreateSerializerV2(pd.BaseModel):
    name: str


class LinkUrlDomainReadSerializerV2(pd.BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    is_base: bool
    name: str

    class Config:
        orm_mode = True
