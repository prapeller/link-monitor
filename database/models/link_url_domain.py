from typing import Union

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from database.models.association import IdentifiedCreatedUpdated


class LinkUrlDomain(IdentifiedCreatedUpdated):
    name: str
    is_base: bool | None = None

    links: Union[list['Link'], None] = None
    seo_users: Union[list['User'], None] = None


class LinkUrlDomainModel(Base):
    __tablename__ = 'link_url_domain'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    name = sa.Column(sa.String(255), index=True)
    is_base = sa.Column(sa.Boolean, default=False)

    links = relationship("LinkModel", cascade='all,delete', back_populates='link_url_domain')
    seo_users = relationship("UserModel", secondary='user_link_url_domain', back_populates='seo_link_url_domains')

    def __repr__(self):
        return f"<LinkUrlDomainModel> (id={self.id}, name={self.name})"

    def __str__(self):
        return f"{self.name}"
