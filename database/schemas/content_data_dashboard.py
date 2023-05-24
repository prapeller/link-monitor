import pydantic as pd
import datetime as dt


class ContentDataUpdateSerializer(pd.BaseModel):
    content_author_id: int | None = None
    month: int | None = None
    year: int | None = None

    pbns_qty: int | None = None

    rate_communication: int | None = None
    rate_quality: int | None = None
    rate_reliability: int | None = None
    comment: str | None = None


class ContentDataCreateSerializer(ContentDataUpdateSerializer):
    content_author_id: int
    month: int
    year: int


class ContentDataReadSerializer(ContentDataCreateSerializer):
    id: int
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    content_teamlead_id: int | None = None

    words_qty: int | None = None
    total_qty: int | None = None
    difference_qty: int | None = None

    rate_avg: int | None = None


class ContentDataReadUsersSerializer(ContentDataReadSerializer):
    content_author: 'UserReadSerializer' = None
    content_teamlead: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


from database.schemas.user import UserReadSerializer

ContentDataReadUsersSerializer.update_forward_refs()
