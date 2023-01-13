from datetime import datetime
from typing import Union

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from database.models.association import IdentifiedCreatedUpdated


class LinkCheck(IdentifiedCreatedUpdated):
    href_is_found: bool | None = None
    href_has_rel: bool | None = None
    rel_has_nofollow: bool | None = None
    rel_has_sponsored: bool | None = None
    meta_robots_has_noindex: bool | None = None
    meta_robots_has_nofollow: bool | None = None
    anchor_text_found: str | None = None
    anchor_count: int | None = None
    ssl_expiration_date: datetime | None = None
    ssl_expires_in_days: int | None = None
    response_text: str | None = None
    response_code: int | None = None
    status: str | None = None
    result_message: str | None = None
    redirect_codes_list: str | None = None
    redirect_url: str | None = None
    link_url_others_count: int | None = None

    link_id: int
    link: Union['User', None] = None


class LinkCheckModel(Base):
    __tablename__ = 'link_check'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    href_is_found = sa.Column(sa.Boolean)
    href_has_rel = sa.Column(sa.Boolean)
    rel_has_nofollow = sa.Column(sa.Boolean)
    rel_has_sponsored = sa.Column(sa.Boolean)
    meta_robots_has_noindex = sa.Column(sa.Boolean)
    meta_robots_has_nofollow = sa.Column(sa.Boolean)
    anchor_text_found = sa.Column(sa.String(700), index=True)
    anchor_count = sa.Column(sa.Integer)
    ssl_expiration_date = sa.Column(sa.DateTime)
    ssl_expires_in_days = sa.Column(sa.Integer)
    result_message = sa.Column(sa.String, index=True)
    response_text = sa.Column(sa.Text)
    response_code = sa.Column(sa.Integer)
    redirect_codes_list = sa.Column(sa.String)
    redirect_url = sa.Column(sa.String(2048), index=True)
    link_url_others_count = sa.Column(sa.Integer)
    status = sa.Column(sa.String(10), index=True)
    check_mode = sa.Column(sa.String(10), nullable=True, index=True)

    link_id = sa.Column(sa.Integer, sa.ForeignKey('link.id'))
    link = relationship("LinkModel", cascade='all,delete', back_populates="link_checks",
                        primaryjoin='LinkCheckModel.link_id==LinkModel.id')

    def __repr__(self):
        return f"<LinkCheckModel> (id={self.id}, link_id={self.link_id})"
