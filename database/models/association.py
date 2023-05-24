import sqlalchemy as sa

from database import Base


class UserLinkUrlDomainAssociation(Base):
    __tablename__ = 'user_link_url_domain'
    __table_args__ = (
        sa.UniqueConstraint(
            'user_id', 'link_url_domain_id', name='unique_user_id_link_url_domain_id'),
        {'extend_existing': True},
    )

    user_id = sa.Column(
        sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
    link_url_domain_id = sa.Column(sa.Integer, sa.ForeignKey('link_url_domain.id'),
                                   primary_key=True)


class PageUrlDomainTagAssociation(Base):
    __tablename__ = 'page_url_domain_tag'
    __table_args__ = (
        sa.UniqueConstraint(
            'page_url_domain_id', 'tag_id', name='unique_page_url_domain_id_tag_id'),
    )

    page_url_domain_id = sa.Column(
        sa.Integer, sa.ForeignKey('page_url_domain.id'), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey('tag.id'), primary_key=True)
