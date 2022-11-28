from typing import Union

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from database.models.association import IdentifiedCreatedUpdated


class User(IdentifiedCreatedUpdated):
    uuid: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_teamlead: bool | None = None
    is_head: bool | None = None
    is_accepting_emails: bool | None = None
    is_accepting_telegram: bool | None = None
    telegram_id: str | None = None
    is_active: bool | None = None
    is_seo: bool | None = None

    teamlead_id: int | None = None
    teamlead: Union['User', None] = None

    linkbuilders: Union[list['User'], None] = None
    links: Union[list['Link'], None] = None
    sent_messages: Union[list['Message'], None] = None
    received_messages: Union[list['Message'], None] = None
    seo_link_url_domains: Union[list['LinkUrlDomain'], None] = None

    def __init__(self,
                 email,
                 first_name,
                 last_name,
                 is_teamlead, is_head,
                 is_accepting_emails,
                 is_accepting_telegram,
                 telegram_id,
                 is_active,
                 is_seo,
                 teamlead_id,

                 id=None,
                 uuid=None,
                 teamlead=None,
                 linkbuilders=None,
                 links=None,
                 sent_messages=None,
                 received_messages=None,
                 seo_link_url_domains=None
                 ):
        self.id = id
        self.uuid = uuid

        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_teamlead = is_teamlead
        self.is_head = is_head
        self.is_accepting_emails = is_accepting_emails
        self.is_accepting_telegram = is_accepting_telegram
        self.telegram_id = telegram_id
        self.is_active = is_active
        self.is_seo = is_seo

        self.teamlead_id = teamlead_id
        self.teamlead = teamlead
        self.linkbuilders = linkbuilders
        self.links = links
        self.sent_messages = sent_messages
        self.received_messages = received_messages
        self.seo_link_url_domains = seo_link_url_domains

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.email == other.email

    def __hash__(self):
        return hash(self.email)


class UserModel(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    uuid = sa.Column(sa.String(50), unique=True, index=True)
    email = sa.Column(sa.String(255), unique=True, index=True)
    first_name = sa.Column(sa.String(50), index=True)
    last_name = sa.Column(sa.String(50), index=True)
    is_head = sa.Column(sa.Boolean, default=False)
    is_teamlead = sa.Column(sa.Boolean, default=False)
    is_seo = sa.Column(sa.Boolean, default=False)
    is_accepting_emails = sa.Column(sa.Boolean, default=False)
    is_accepting_telegram = sa.Column(sa.Boolean, default=False)
    telegram_id = sa.Column(sa.String(255))
    is_active = sa.Column(sa.Boolean, default=True)

    teamlead_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    teamlead = relationship("UserModel", back_populates='linkbuilders', remote_side='UserModel.id')

    linkbuilders = relationship("UserModel", back_populates='teamlead')
    links = relationship("LinkModel", back_populates='user')
    sent_messages = relationship("MessageModel", back_populates='from_user',
                                 primaryjoin='MessageModel.from_user_id==UserModel.id')
    received_messages = relationship("MessageModel", back_populates='to_user',
                                     primaryjoin='MessageModel.to_user_id==UserModel.id')

    seo_link_url_domains = relationship("LinkUrlDomainModel", secondary='user_link_url_domain',
                                        back_populates='seo_users')

    @hybrid_property
    def seo_link_url_domains_id(self):
        return [link_url_domain.id for link_url_domain in self.seo_link_url_domains]

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
        return f'<UserModel> (id={self.id}, email={self.email})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def __eq__(self, other):
        if not isinstance(other, UserModel):
            return False
        return self.email == other.email

    def __hash__(self):
        return hash(self.email)
