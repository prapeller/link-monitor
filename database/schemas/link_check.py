from datetime import datetime

import pydantic as pd


class LinkCheckCreateSerializer(pd.BaseModel):
    link_id: int
    href_is_found: bool | None = None
    href_has_rel: bool | None = None
    rel_has_nofollow: bool | None = None
    rel_has_sponsored: bool | None = None
    meta_robots_has_noindex: bool | None = None
    meta_robots_has_nofollow: bool | None = None
    anchor_text_found: str | None = None
    anchor_count: int | None = None
    ssl_expiration_date: datetime | None = None
    ssl_expires_in_days: int | None = None
    response_text: str | None = None
    response_code: int | None = None
    status: str | None = None
    result_message: str | None = None
    redirect_codes_list: str | None = None
    redirect_url: str | None = None
    link_url_others_count: int | None = None


class LinkCheckReadSerializer(LinkCheckCreateSerializer):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class LinkCheckReadLinkSerializer(LinkCheckReadSerializer):
    link: 'LinkReadSerializer'

    class Config:
        orm_mode = True


from database.schemas.link import LinkReadSerializer

LinkCheckReadLinkSerializer.update_forward_refs()
