import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from database.models.link_check import LinkCheckModel
from database.models.link_url_domain import LinkUrlDomainModel


class LinkModel(Base):
    __tablename__ = 'link'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    page_url = sa.Column(sa.String(2048), nullable=False, index=True)
    anchor = sa.Column(sa.String(512), nullable=False, index=True)
    _link_url = sa.Column('link_url', sa.String(2048), nullable=False, index=True)
    da = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)
    dr = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)
    price = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True, index=True)
    screenshot_url = sa.Column(sa.String(512), nullable=True, index=True)
    contact = sa.Column(sa.String(255), nullable=True, index=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    user = relationship("UserModel", back_populates='links')

    page_url_domain_id = sa.Column(sa.Integer, sa.ForeignKey('page_url_domain.id'))
    page_url_domain = relationship("PageUrlDomainModel", back_populates='links')

    link_url_domain_id = sa.Column(sa.Integer, sa.ForeignKey('link_url_domain.id'))
    link_url_domain = relationship("LinkUrlDomainModel", back_populates='links')

    link_checks = relationship("LinkCheckModel", cascade='all,delete', back_populates='link', primaryjoin='LinkModel.id==LinkCheckModel.link_id')

    link_check_last_id = sa.Column(sa.Integer, sa.ForeignKey('link_check.id'))
    link_check_last = relationship("LinkCheckModel", primaryjoin='LinkModel.link_check_last_id==LinkCheckModel.id')
    link_check_last_status = sa.Column(sa.String(10), index=True)
    link_check_last_result_message = sa.Column(sa.String, index=True)

    @hybrid_property
    def link_url(self):
        return self._link_url

    @link_url.setter
    def link_url(self, link_url: str):
        self._link_url = link_url + '/' if isinstance(link_url, str) and not link_url.endswith('/') else link_url

    # @hybrid_property
    # def link_check_last(self):
    #     link_check_last = None
    #     if self.link_checks:
    #         if self.link_check_last_id:
    #             return [link_check for link_check in self.link_checks if link_check.id == self.link_check_last_id][0]
    #         else:
    #             link_checks_sorted = sorted(self.link_checks, key=lambda x: x.id)
    #             link_check_last = link_checks_sorted[-1]
    #     return link_check_last

    # @link_check_last.expression
    # def link_check_last(self):
    #     return sa.select(LinkCheckModel.id).where(LinkCheckModel.link_id == id).order_by(desc(LinkCheckModel.id)).limit(1)


    # @hybrid_property
    # def link_check_last_result_message(self):
    #     if self.link_check_last:
    #         return self.link_check_last.result_message
    #     else:
    #         return None

    # @link_check_last_result_message.expression
    # def link_check_last_result_message(cls):
    #     return sa.select(LinkCheckModel.result_message).where(LinkCheckModel.link_id == cls.id).order_by(desc(LinkCheckModel.id)).limit(1)

    # @hybrid_property
    # def link_check_last_status(self):
    #     if self.link_check_last:
    #         return self.link_check_last.status
    #     else:
    #         return None

    # @link_check_last_status.expression
    # def link_check_last_status(cls):
    #     return sa.select(LinkCheckModel.status).where(LinkCheckModel.link_id == cls.id).order_by(desc(LinkCheckModel.id)).limit(1)

    @hybrid_property
    def link_check_last_created_at(self):
        if self.link_check_last:
            return self.link_check_last.created_at
        else:
            return None

    @link_check_last_created_at.expression
    def link_check_last_created_at(cls):
        return sa.select(LinkCheckModel.created_at).where(LinkCheckModel.id == cls.link_check_last_id)

    @hybrid_property
    def link_url_domain_name(self):
        if self.link_url_domain:
            return self.link_url_domain.name
        else:
            return None

    @link_url_domain_name.expression
    def link_url_domain_name(cls):
        return sa.select(LinkUrlDomainModel.name).where(LinkUrlDomainModel.id == cls.link_url_domain_id)

    __table_args__ = (
        sa.UniqueConstraint('page_url', 'anchor', 'link_url', name='unique_page_url_anchor_link_url'),
    )

    def __str__(self):
        return f"Link with page_url: {self.page_url}"

    def __repr__(self):
        return f"LinkModel(id={self.id}, link_url_domain={self.link_url_domain})"
