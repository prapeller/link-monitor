import sqlalchemy as sa

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class TaskContentModel(Base):
    __tablename__ = 'task_content'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=True)

    # Sent to teamlead / Sent to author / Text written / In Edit / Confirmed / Closed
    status = sa.Column(sa.String, nullable=False, index=True)
    page_url_domain_name = sa.Column(sa.String(2048), nullable=False, index=True)
    link_url = sa.Column(sa.String(2048), nullable=False, index=True)
    anchor = sa.Column(sa.String(512), nullable=False, index=True)
    language_full_name = sa.Column(sa.String(20), nullable=False, index=True)
    words_qty = sa.Column(sa.Integer, nullable=False)
    requirements = sa.Column(sa.String, nullable=True)

    words_qty_fact = sa.Column(sa.Integer, nullable=True)
    text_url = sa.Column(sa.String(2048), nullable=True)
    edits = sa.Column(sa.String, nullable=True)
    page_url = sa.Column(sa.String(2048), nullable=True, index=True)
    closed_at = sa.Column(sa.DateTime, nullable=True)

    content_linkbuilder_id = sa.Column(sa.Integer, sa.ForeignKey('user.id')) # creator
    content_linkbuilder = relationship("UserModel", back_populates='content_linkbuilder_tasks',
                               primaryjoin='TaskContentModel.content_linkbuilder_id==UserModel.id')

    content_teamlead_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_teamlead = relationship("UserModel", back_populates='content_teamlead_tasks',
                               primaryjoin='TaskContentModel.content_teamlead_id==UserModel.id')

    content_author_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    content_author = relationship("UserModel", back_populates='content_author_tasks',
                               primaryjoin='TaskContentModel.content_author_id==UserModel.id')

    # if one of the following == False - then appointee should view task (it will be selected as 'should view')
    # when task is just created and there's no author appointed yet, teamlead already can view it
    content_linkbuilder_viewed = sa.Column(sa.Boolean, nullable=False, default=True)
    content_teamlead_viewed = sa.Column(sa.Boolean, nullable=False, default=True)
    content_author_viewed = sa.Column(sa.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<TaskContentModel> ({self.id=:}, {self.status=:}, {self.page_url_domain_name=:}, {self.link_url=:})"
