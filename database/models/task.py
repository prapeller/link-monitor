import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database import IdentifiedCreatedUpdated, Base


class TaskContentModel(IdentifiedCreatedUpdated, Base):
    """
    status choices: Sent to teamlead / Sent to author / Text written / In Edit / Closed
    content_linkbuilder = creator
    content_teamlead = teamlead chosen by content_linkbuilder
    content_author = author chosen by teamlead
    """
    __tablename__ = 'task_content'

    status = sa.Column(sa.String, nullable=False, index=True)
    page_url_domain_name = sa.Column(sa.String(2048), nullable=False, index=True)
    link_url = sa.Column(sa.String(2048), nullable=False, index=True)
    anchor = sa.Column(sa.String(512), nullable=False, index=True)
    language_full_name = sa.Column(sa.String(20), nullable=False, index=True)
    words_qty = sa.Column(sa.Integer, nullable=False)
    requirements = sa.Column(sa.String, nullable=True)

    words_qty_fact = sa.Column(sa.Integer, default=0)
    text_url = sa.Column(sa.String(2048), nullable=True)
    edits = sa.Column(sa.String, nullable=True)
    page_url = sa.Column(sa.String(2048), nullable=True, index=True)
    deadline_at = sa.Column(sa.DateTime, nullable=True)
    closed_at = sa.Column(sa.DateTime, nullable=True)

    content_linkbuilder_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_linkbuilder = relationship("UserModel", back_populates='content_linkbuilder_tasks',
                                       primaryjoin='TaskContentModel.content_linkbuilder_id==UserModel.id')

    content_teamlead_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_teamlead = relationship("UserModel", back_populates='content_teamlead_tasks',
                                    primaryjoin='TaskContentModel.content_teamlead_id==UserModel.id')

    content_author_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_author = relationship("UserModel", back_populates='content_author_tasks',
                                  primaryjoin='TaskContentModel.content_author_id==UserModel.id')

    content_linkbuilder_viewed = sa.Column(sa.Boolean, nullable=False, default=True)
    content_teamlead_viewed = sa.Column(sa.Boolean, nullable=False, default=True)
    content_author_viewed = sa.Column(sa.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<TaskContentModel> ({self.id=:}, {self.status=:}, {self.page_url_domain_name=:}, {self.link_url=:})"
