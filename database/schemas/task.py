import datetime as dt

import pydantic as pd

from core.config import settings
from core.enums import TaskContentStatusEnum
from database.models.task import TaskContentModel


class TaskContentUpdateSerializer(pd.BaseModel):
    created_at: dt.datetime | None = None
    deadline_at: dt.datetime | None = None

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
    closed_at: dt.datetime | None = None

    content_linkbuilder_viewed: bool | None = None
    content_teamlead_viewed: bool | None = None
    content_author_viewed: bool | None = None

    content_linkbuilder_id: int | None = None
    content_teamlead_id: int | None = None
    content_author_id: int | None = None

    def set_deadline(self) -> None:
        if self.deadline_at is None:
            assert self.created_at is not None, 'task.created_at must not be None'
            deadline_at = self.created_at

            if self.language_full_name in ('English', 'French', 'German'):
                business_days_to_add = settings.BUSINESS_DAYS_TO_ADD_SHORT
            else:
                business_days_to_add = settings.BUSINESS_DAYS_TO_ADD_LONG

            while business_days_to_add > 0:
                deadline_at += dt.timedelta(days=1)
                if deadline_at.weekday() >= 5:
                    continue
                business_days_to_add -= 1
            self.deadline_at = deadline_at

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

    def create(self, repo, current_user):
        self.content_linkbuilder_id = current_user.id
        self.content_teamlead_viewed = False
        self.set_deadline()
        task_content = repo.create(TaskContentModel, self)
        return task_content


class TaskContentReadSerializer(TaskContentUpdateSerializer):
    id: int
    created_at: dt.datetime
    updated_at: dt.datetime | None = None


class TaskContentReadUsersSerializer(TaskContentReadSerializer):
    content_linkbuilder: 'UserReadSerializer' = None
    content_teamlead: 'UserReadSerializer' = None
    content_author: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


from database.schemas.user import UserReadSerializer

TaskContentReadUsersSerializer.update_forward_refs()
