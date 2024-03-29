import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from database import IdentifiedCreatedUpdated, Base
from database.models.message import MessageModel


class UserModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'user'

    uuid = sa.Column(sa.String(50), unique=True, index=True)
    email = sa.Column(sa.String(255), unique=True, index=True)
    first_name = sa.Column(sa.String(50), index=True)
    last_name = sa.Column(sa.String(50), index=True)
    is_head = sa.Column(sa.Boolean, default=False)
    is_teamlead = sa.Column(sa.Boolean, default=False)
    is_seo = sa.Column(sa.Boolean, default=False)
    is_content_head = sa.Column(sa.Boolean, default=False)
    is_content_teamlead = sa.Column(sa.Boolean, default=False)
    is_content_author = sa.Column(sa.Boolean, default=False)
    is_accepting_emails = sa.Column(sa.Boolean, default=False)
    is_accepting_telegram = sa.Column(sa.Boolean, default=False)
    telegram_id = sa.Column(sa.String(255))
    is_active = sa.Column(sa.Boolean, default=True)
    timezone = sa.Column(sa.String(10))

    teamlead_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    teamlead = relationship(
        "UserModel",
        primaryjoin='UserModel.id==UserModel.teamlead_id',
        remote_side='UserModel.id',
        backref=backref('linkbuilders'), )

    content_teamlead_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_teamlead = relationship(
        "UserModel",
        primaryjoin='UserModel.id==UserModel.content_teamlead_id',
        remote_side='UserModel.id',
        backref=backref('content_authors'), )

    links = relationship(
        "LinkModel", back_populates='user')

    sent_messages = relationship(
        "MessageModel", back_populates='from_user',
        primaryjoin='MessageModel.from_user_id==UserModel.id')

    accepted_messages: list[MessageModel] = relationship(
        "MessageModel", back_populates='to_user',
        primaryjoin='MessageModel.to_user_id==UserModel.id')

    seo_link_url_domains = relationship(
        "LinkUrlDomainModel", secondary='user_link_url_domain',
        back_populates='seo_users')

    content_linkbuilder_tasks = relationship(
        "TaskContentModel",
        back_populates='content_linkbuilder',
        primaryjoin='TaskContentModel.content_linkbuilder_id==UserModel.id')

    content_teamlead_tasks = relationship(
        "TaskContentModel", back_populates='content_teamlead',
        primaryjoin='TaskContentModel.content_teamlead_id==UserModel.id')

    content_author_tasks = relationship(
        "TaskContentModel", back_populates='content_author',
        primaryjoin='TaskContentModel.content_author_id==UserModel.id')

    content_dashboard_data = relationship("ContentDataModel", back_populates='content_author',
                                          primaryjoin='UserModel.id==ContentDataModel.content_author_id')

    @hybrid_property
    def seo_link_url_domains_id(self):
        return [link_url_domain.id for link_url_domain in self.seo_link_url_domains]

    @hybrid_property
    def linkbuilders_id(self):
        return [linkbuilder.id for linkbuilder in self.linkbuilders]

    @linkbuilders_id.expression
    def linkbuilders_id(cls):
        return sa.select(UserModel.id).where(UserModel.teamlead_id == cls.id)

    @hybrid_property
    def pending_messages(self):
        return [message for message in self.accepted_messages if not message.is_notified]

    @pending_messages.expression
    def pending_messages(cls):
        return sa.select(MessageModel).where(
            sa.and_(MessageModel.to_user == cls.id, MessageModel.is_notified == False))

    @hybrid_property
    def content_authors_id(self):
        return [content_author.id for content_author in self.content_authors]

    @content_authors_id.expression
    def content_authors_id(cls):
        return sa.select(UserModel.id).where(UserModel.content_teamlead_id == cls.id)

    @hybrid_property
    def links_id(self):
        return [link.id for link in self.links]

    @hybrid_property
    def teamlead_name(self):
        return f'{self.teamlead.first_name} {self.teamlead.last_name}' if self.teamlead else ''

    def __repr__(self):
        return f'<UserModel> ({self.id=:}, {self.email=:})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def __eq__(self, other):
        if not isinstance(other, UserModel):
            return False
        return self.email == other.email

    def __hash__(self):
        return hash(self.email)
