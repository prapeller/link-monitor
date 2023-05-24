import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import IdentifiedCreatedUpdated, Base


class LinkUrlDomainModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'link_url_domain'

    name = sa.Column(sa.String(255), index=True)
    is_base = sa.Column(sa.Boolean, default=False)

    links = relationship("LinkModel", cascade='all,delete', back_populates='link_url_domain')
    seo_users = relationship("UserModel", secondary='user_link_url_domain',
                             back_populates='seo_link_url_domains')

    def __repr__(self):
        return f"<LinkUrlDomainModel> ({self.id=:}, {self.name}=:)"

    def __str__(self):
        return f"{self.name}"
