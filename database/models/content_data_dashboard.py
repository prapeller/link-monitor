import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import tuple_

from core.config import settings
from database import Base, IdentifiedCreatedUpdated
from database.models.task import TaskContentModel


class ContentDataModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'content_data'

    content_author_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_author = relationship("UserModel", back_populates='content_dashboard_data',
                                  primaryjoin='ContentDataModel.content_author_id==UserModel.id')

    year = sa.Column(sa.SmallInteger)
    month = sa.Column(sa.SmallInteger)

    pbns_qty = sa.Column(sa.Integer, default=0)

    rate_communication = sa.Column(sa.SmallInteger, default=0)
    rate_quality = sa.Column(sa.SmallInteger, default=0)
    rate_reliability = sa.Column(sa.SmallInteger, default=0)
    comment = sa.Column(sa.Text, default='')

    @hybrid_property
    def year_month(self):
        return self.year, self.month

    @year_month.expression
    def year_month(cls):
        return tuple_(cls.year, cls.month)

    @hybrid_property
    def content_teamlead_id(self):
        return self.content_author.content_teamlead_id

    @hybrid_property
    def content_teamlead(self):
        return self.content_author.content_teamlead

    @hybrid_property
    def words_qty(self):
        return sum([task.words_qty_fact for task in self.content_author.content_author_tasks
                    if (task.created_at.year, task.created_at.month) == self.year_month])

    @words_qty.expression
    def words_qty(cls):
        return sa.select(sa.func.sum(TaskContentModel.words_qty_fact) \
                         .where(TaskContentModel.content_author_id == cls.content_author_id and
                                sa.extract('year', TaskContentModel.created_at) == cls.year and
                                sa.extract('month', TaskContentModel.created_at) == cls.month))

    @hybrid_property
    def total_qty(self):
        return self.pbns_qty + self.words_qty

    @hybrid_property
    def rate_avg(self):
        return (self.rate_communication + self.rate_quality + self.rate_reliability) / 3

    @hybrid_property
    def difference_qty(self):
        return self.total_qty - settings.CONTENT_AUTHOR_MONTH_WORDS_QTY_PLAN

    def __str__(self):
        return f"{self.content_author=:}, {self.year=:}, {self.month=:}"

    __table_args__ = (
        sa.UniqueConstraint('content_author_id', 'year', 'month', name='unique_content_author_id_year_month'),
    )
