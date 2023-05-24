from datetime import datetime

import pydantic as pd


class MessageUpdateSerializer(pd.BaseModel):
    header: str | None = None
    text: str | None = None
    is_read: bool | None = None
    is_notified: bool | None = None

    to_user_id: int | None = None

    class Config:
        orm_mode = True


class MessageCreateSerializer(MessageUpdateSerializer):
    from_user_id: int | None = None

    class Config:
        orm_mode = True


class MessageReadSerializer(MessageCreateSerializer):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class MessageReadFromUserSerializer(MessageReadSerializer):
    from_user: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


class MessageReadToUserSerializer(MessageReadSerializer):
    to_user: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


from database.schemas.user import UserReadSerializer

MessageReadFromUserSerializer.update_forward_refs()
MessageReadToUserSerializer.update_forward_refs()
