import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class PageUrlDomainModel(Base):
    __tablename__ = 'page_url_domain'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    name = sa.Column(sa.String(255), index=True)

    links = relationship("LinkModel", back_populates='page_url_domain')

    def __repr__(self):
        return f"PageUrlDomainModel(id={self.id}, name={self.name})"
