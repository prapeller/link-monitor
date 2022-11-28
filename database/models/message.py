from typing import Union

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from database.models.association import IdentifiedCreatedUpdated


class Message(IdentifiedCreatedUpdated):
    header: str | None = None
    text: str | None = None
    is_read: bool | None = None

    from_user_id: int | None = None
    from_user: Union['User', None] = None
    to_user_id: int | None = None
    to_user: Union['User', None] = None


class MessageModel(Base):
    __tablename__ = 'message'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    header = sa.Column(sa.String)
    text = sa.Column(sa.Text)
    is_read = sa.Column(sa.Boolean, default=False)

    from_user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), default=None)
    from_user = relationship("UserModel", back_populates='sent_messages',
                             primaryjoin='UserModel.id==MessageModel.from_user_id', post_update=True)

    to_user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    to_user = relationship("UserModel", back_populates='received_messages',
                           primaryjoin='UserModel.id==MessageModel.to_user_id', post_update=True)

    def __repr__(self):
        return f"<MessageModel> (id={self.id}, from_user={self.from_user}, to_user={self.to_user}, header={self.header})"
