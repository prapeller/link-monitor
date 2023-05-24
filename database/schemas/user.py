import datetime as dt

import pydantic as pd

from core.enums import UTCTimeZonesEnum


class UserUpdateSerializer(pd.BaseModel):
    email: pd.EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_teamlead: bool | None = None
    is_head: bool | None = None
    is_content_teamlead: bool | None = None
    is_content_author: bool | None = None
    is_content_head: bool | None = None
    is_accepting_emails: bool | None = None
    is_accepting_telegram: bool | None = None
    telegram_id: str | None = None
    teamlead_id: int | None = None
    content_teamlead_id: int | None = None
    is_active: bool | None = None
    is_seo: bool | None = None
    timezone: UTCTimeZonesEnum | None = None

    def lower_email(self):
        if self.email is not None:
            self.email = self.email.lower()


class UserCreateSerializer(UserUpdateSerializer):
    email: pd.EmailStr
    uuid: str | None = None


class UserReadSerializer(UserCreateSerializer):
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    is_active: bool

    seo_link_url_domains_id: list[int] = []
    linkbuilders_id: list[int] = []
    content_authors_id: list[int] = []

    class Config:
        orm_mode = True


class UserReadTeamleadSerializer(UserReadSerializer):
    teamlead: 'UserReadSerializer' = None
    content_teamlead: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


class DashboardUserDataResponseModel(pd.BaseModel):
    user: str
    mean_da: float
    mean_dr: float
    mean_price: float
    total_links_count: int
    green_links_count: int
    red_links_count: int
    period_link_growth_green: int
    period_link_growth_red: int


UserReadTeamleadSerializer.update_forward_refs()
