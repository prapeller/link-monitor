import sqlalchemy as sa
from sqlalchemy.orm import mapper

from database import Base
from database.models import user, link, link_check, message, link_url_domain, page_url_domain


def init_models():
    from database.models import user
    from database.models import tag
    from database.models import link
    from database.models import link_check
    from database.models import link_url_domain
    from database.models import page_url_domain
    from database.models import message
    from database.models import association


def start_mappers(engine):
    mapper(user.User, sa.Table('user', Base.metadata, autoload_with=engine))
    mapper(link.Link, sa.Table('link', Base.metadata, autoload_with=engine))
    mapper(link_check.LinkCheck, sa.Table('link_check', Base.metadata, autoload_with=engine))
    mapper(message.Message, sa.Table('message', Base.metadata, autoload_with=engine))
    mapper(link_url_domain.LinkUrlDomain, sa.Table('link_url_domain', Base.metadata, autoload_with=engine))
    mapper(page_url_domain.PageUrlDomain, sa.Table('page_url_domain', Base.metadata, autoload_with=engine))
