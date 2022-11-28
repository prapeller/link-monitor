from datetime import datetime
from typing import Union

import pydantic as pd


class PageUrlDomainUpdateSerializer(pd.BaseModel):
    name: str | None = None
    tags_id: list[int] | None = []


class PageUrlDomainCreateSerializer(PageUrlDomainUpdateSerializer):
    name: str


class PageUrlDomainReadSerializer(PageUrlDomainCreateSerializer):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class BaseCheckResponseModel(pd.BaseModel):
    present: list[str]
    not_present: list[str]


class PUDomainReadLastLinkSerializer(PageUrlDomainReadSerializer):
    link_da_last: float | None = None
    link_dr_last: float | None = None
    link_created_at_last: datetime | None = None
    link_price_avg: float | None = None

    language_tags: Union[list['TagReadSerializer'], list] = []
    country_tags: Union[list['TagReadSerializer'], list] = []

    class Config:
        orm_mode = True


class PUDomainReadLastLinkManyTotalCountResponseModel(pd.BaseModel):
    domains_read_last_links: list['PUDomainReadLastLinkSerializer']
    total_domains_count: int


from database.schemas.tag import TagReadSerializer
PUDomainReadLastLinkSerializer.update_forward_refs()
