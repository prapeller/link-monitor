import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import IdentifiedCreatedUpdated, Base


class MessageModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'message'

    header = sa.Column(sa.String)
    text = sa.Column(sa.Text)
    is_read = sa.Column(sa.Boolean, default=False)
    is_notified = sa.Column(sa.Boolean, default=False)

    from_user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), default=None)
    from_user = relationship("UserModel", back_populates='sent_messages',
                             primaryjoin='UserModel.id==MessageModel.from_user_id',
                             post_update=True)

    to_user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    to_user = relationship("UserModel", back_populates='accepted_messages',
                           primaryjoin='UserModel.id==MessageModel.to_user_id',
                           post_update=True)

    def __repr__(self):
        return f"<MessageModel> ({self.id=:}, {self.from_user=:}, {self.to_user:=}, {self.header=:})"
