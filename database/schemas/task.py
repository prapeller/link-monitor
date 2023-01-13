from datetime import datetime

import pydantic as pd

from core.enums import TaskContentStatusEnum


class TaskContentUpdateSerializer(pd.BaseModel):
    status: TaskContentStatusEnum | None = None
    page_url_domain_name: str | None = None
    link_url: pd.HttpUrl | None = None
    anchor: str | None = None
    language_full_name: str | None = None
    words_qty: int | None = None
    requirements: str | None = None

    words_qty_fact: int | None = None
    text_url: pd.HttpUrl | None = None
    edits: str | None = None
    page_url: pd.HttpUrl | None = None
    closed_at: datetime | None = None

    content_linkbuilder_viewed: bool | None = None
    content_teamlead_viewed: bool | None = None
    content_author_viewed: bool | None = None

    content_linkbuilder_id: int | None = None
    content_teamlead_id: int | None = None
    content_author_id: int | None = None

    class Config:
        orm_mode = True


class TaskContentCreateSerializer(TaskContentUpdateSerializer):
    status: TaskContentStatusEnum
    page_url_domain_name: str
    link_url: pd.HttpUrl
    anchor: str
    language_full_name: str
    words_qty: int
    requirements: str

    content_teamlead_id: int


class TaskContentReadSerializer(TaskContentUpdateSerializer):
    id: int
    created_at: datetime
    updated_at: datetime | None = None


class TaskContentReadUsersSerializer(TaskContentReadSerializer):
    content_linkbuilder: 'UserReadSerializer' = None
    content_teamlead: 'UserReadSerializer' = None
    content_author: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


from database.schemas.user import UserReadSerializer

TaskContentReadUsersSerializer.update_forward_refs()
