import sqlalchemy as sa

from database import IdentifiedCreatedUpdated, Base


class TagModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'tag'

    name = sa.Column(sa.String)
    full_name = sa.Column(sa.String)
    ref_property = sa.Column(sa.String)

    __table_args__ = (
        sa.UniqueConstraint('name', 'ref_property', name='unique_name_ref_property'),
    )

    def __repr__(self):
        return f"<TagModel> ({self.id=:}, {self.name=:}, {self.full_name=:})"
