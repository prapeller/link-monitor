import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from database import IdentifiedCreatedUpdated, Base
from database.models.link_url_domain import LinkUrlDomainModel


class LinkModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'link'

    page_url = sa.Column(sa.String(2048), nullable=False, index=True)
    anchor = sa.Column(sa.String(512), nullable=False, index=True)
    link_url = sa.Column(sa.String(2048), nullable=False, index=True)
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

    link_checks = relationship("LinkCheckModel", cascade='all,delete', back_populates='link',
                               primaryjoin='LinkModel.id==LinkCheckModel.link_id')

    link_check_last_id = sa.Column(sa.Integer, sa.ForeignKey('link_check.id'))
    link_check_last = relationship("LinkCheckModel",
                                   primaryjoin='LinkModel.link_check_last_id==LinkCheckModel.id',
                                   post_update=True)
    link_check_last_status = sa.Column(sa.String(10), index=True)
    link_check_last_result_message = sa.Column(sa.String, index=True)
    link_check_last_check_mode = sa.Column(sa.String(10), nullable=True, index=True)
    link_check_last_created_at = sa.Column(sa.DateTime, nullable=True)

    @hybrid_property
    def link_url_domain_name(self):
        if self.link_url_domain:
            return self.link_url_domain.name
        else:
            return None

    @link_url_domain_name.expression
    def link_url_domain_name(cls):
        return sa.select(LinkUrlDomainModel.name).where(
            LinkUrlDomainModel.id == cls.link_url_domain_id)

    __table_args__ = (
        sa.UniqueConstraint('page_url', 'anchor', 'link_url',
                            name='unique_page_url_anchor_link_url'),
    )

    def __str__(self):
        return f"Link ({self.id=:}, {self.page_url=:})"

    def __repr__(self):
        return f"<LinkModel> ({self.id=:}, {self.link_url_domain=:})"
