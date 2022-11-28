from typing import Union

import sqlalchemy as sa

from sqlalchemy.sql import func

from database import Base
from database.models.association import IdentifiedCreatedUpdated


class Tag(IdentifiedCreatedUpdated):
    name: str | None = None


class TagModel(Base):
    __tablename__ = 'tag'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    name = sa.Column(sa.String)
    full_name = sa.Column(sa.String)
    ref_property = sa.Column(sa.String)

    __table_args__ = (
        sa.UniqueConstraint('name', 'ref_property', name='unique_name_ref_property'),
    )


    def __repr__(self):
        return f"<TagModel> (id={self.id}, name={self.name}, full_name: {self.full_name})"
