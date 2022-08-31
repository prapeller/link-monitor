import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class UserModel(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    uuid = sa.Column(sa.String(50), unique=True, index=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    email = sa.Column(sa.String(255), unique=True, index=True)
    first_name = sa.Column(sa.String(50), index=True)
    last_name = sa.Column(sa.String(50), index=True)
    is_head = sa.Column(sa.Boolean, default=False)
    is_teamlead = sa.Column(sa.Boolean, default=False)
    is_accepting_emails = sa.Column(sa.Boolean, default=False)
    is_accepting_telegram = sa.Column(sa.Boolean, default=False)
    telegram_id = sa.Column(sa.String(255))
    is_active = sa.Column(sa.Boolean, default=True)

    teamlead_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    teamlead = relationship("UserModel", back_populates='linkbuilders', remote_side='UserModel.id')

    linkbuilders = relationship("UserModel", back_populates='teamlead')
    links = relationship("LinkModel", back_populates='user')

    @hybrid_property
    def linkbuilders_id(self):
        return [linkbuilder.id for linkbuilder in self.linkbuilders]

    @hybrid_property
    def links_id(self):
        return [link.id for link in self.links]

    @hybrid_property
    def teamlead_name(self):
        return f'{self.teamlead.first_name} {self.teamlead.last_name}' if self.teamlead else ''

    def __repr__(self):
        return f'UserModel(id={self.id}, email={self.email})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
