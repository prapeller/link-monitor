from datetime import datetime

import pydantic as pd


class LinkUpdateSerializer(pd.BaseModel):
    page_url: pd.HttpUrl | None = None
    anchor: str | None = None
    link_url: pd.HttpUrl | None = None
    da: float | None = None
    dr: float | None = None
    price: float | None = None
    contact: str | None = None
    screenshot_url: pd.HttpUrl | None = None

    user_id: int | None = None


class LinkCreateSerializer(LinkUpdateSerializer):
    page_url: pd.HttpUrl
    anchor: str
    link_url: pd.HttpUrl
    da: float | None = None
    dr: float | None = None
    price: float | None = None
    contact: str | None = None

    @pd.validator('link_url')
    def link_url_ends_with_backslash(cls, v):
        if not v.endswith('/'):
            raise ValueError('must end with "/"')
        return v


class LinkCreateWithDomainsSerializer(LinkCreateSerializer):
    created_at: datetime = None
    link_url_domain_id: int | None = None
    page_url_domain_id: int | None = None


class LinkReadSerializer(LinkUpdateSerializer):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    link_url_domain_id: int | None = None
    page_url_domain_id: int | None = None


class LinkReadLinkcheckLastAndDomainsSerializer(LinkReadSerializer):
    link_check_last: 'LinkCheckReadSerializer' = None
    page_url_domain: 'PageUrlDomainReadSerializer' = None
    link_url_domain: 'LinkUrlDomainReadSerializer' = None

    class Config:
        orm_mode = True


class LinkReadLclDomainsUserSerializer(LinkReadLinkcheckLastAndDomainsSerializer):
    user: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


class LinkReadManyTotalCountResponseModel(pd.BaseModel):
    links: list[LinkReadLinkcheckLastAndDomainsSerializer]
    total_links_count: int


class LinkReadSingleTaskIdResponseModel(pd.BaseModel):
    link: LinkReadLinkcheckLastAndDomainsSerializer
    task_id: str


class LinkReadManyTaskIdResponseModel(pd.BaseModel):
    links: list[LinkReadLinkcheckLastAndDomainsSerializer]
    task_id: str


class LinkReadMessageTaskIdResponseModel(pd.BaseModel):
    message: str = 'ok'
    task_id: str


class LinkReadMessageTaskIdListResponseModel(pd.BaseModel):
    message: str = 'ok'
    task_id: list[str]


class LinkReadMessageResponseModel(pd.BaseModel):
    message: str = 'ok'


class LinkReadTaskIdResponseModel(pd.BaseModel):
    task_id: str


from database.schemas.user import UserReadSerializer
from database.schemas.page_url_domain import PageUrlDomainReadSerializer
from database.schemas.link_url_domain import LinkUrlDomainReadSerializer
from database.schemas.link_check import LinkCheckReadSerializer

LinkReadLclDomainsUserSerializer.update_forward_refs()
LinkReadLinkcheckLastAndDomainsSerializer.update_forward_refs()
