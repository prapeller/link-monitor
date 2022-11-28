from datetime import datetime

import pydantic as pd


class UserUpdateSerializer(pd.BaseModel):
    email: pd.EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_teamlead: bool | None = None
    is_head: bool | None = None
    is_accepting_emails: bool | None = None
    is_accepting_telegram: bool | None = None
    telegram_id: str | None = None
    teamlead_id: int | None = None
    is_active: bool | None = None
    is_seo: bool | None = None


class UserCreateSerializer(UserUpdateSerializer):
    email: pd.EmailStr
    uuid: str | None = None


class UserReadSerializer(UserCreateSerializer):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime | None = None

    is_active: bool

    seo_link_url_domains_id: list[int] = []
    linkbuilders_id: list[int] = []

    class Config:
        orm_mode = True


class UserReadTeamleadSerializer(UserReadSerializer):
    teamlead: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


# class UserReadTeamleadNameSerializer(UserReadTeamleadSerializer):
#     teamlead_name: str | None = None
#
#     class Config:
#         orm_mode = True


# class UserReadLinksSerializer(UserCreateSerializer):
#     id: int
#     uuid: str
#     created_at: datetime
#     updated_at: datetime | None = None
#
#     is_active: bool
#
#     seo_link_url_domains_id: list[int] = []
#     linkbuilders_id: list[int] = []
#     links_id: list[int] = []
#
#     class Config:
#         orm_mode = True


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
