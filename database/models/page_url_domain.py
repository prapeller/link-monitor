from typing import Union
from statistics import mean

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

from database import Base
from database.models.link import LinkModel
from database.models.association import IdentifiedCreatedUpdated, PageUrlDomainTagAssociation
from database.models.tag import Tag, TagModel


class PageUrlDomain(IdentifiedCreatedUpdated):
    name: str

    links: Union[list['Link'], None] = None
    tags: Union[list['Tag'], None] = None


class PageUrlDomainModel(Base):
    __tablename__ = 'page_url_domain'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime)

    name = sa.Column(sa.String(255), index=True)

    link_da_last = sa.Column(sa.Numeric(precision=10, scale=2))
    link_dr_last = sa.Column(sa.Numeric(precision=10, scale=2))
    link_created_at_last = sa.Column(sa.DateTime)
    link_price_avg = sa.Column(sa.Numeric(precision=10, scale=2))

    links = relationship("LinkModel", back_populates='page_url_domain')
    tags = relationship('TagModel', secondary='page_url_domain_tag')

    @property
    def sorted_links(self):
        return sorted(self.links, key=lambda x: x.id)

    @hybrid_property
    def links_id(self):
        return [link.id for link in self.links]

    @links_id.expression
    def links_id(cls):
        return sa.select(LinkModel.id).filter(LinkModel.page_url_domain_id == cls.id)

    def update_link_price_avg(self):
        link_prices = []
        for link in self.links:
            if link.price is not None:
                link_prices.append(link.price)
        if link_prices:
            link_price_avg = round(float(mean(link_prices)), 2)
        else:
            link_price_avg = 0
        self.link_price_avg = link_price_avg

    def update_pudomain_link_last(self, link_last: LinkModel) -> None:
        self.link_created_at_last = link_last.created_at
        if link_last.dr is not None:
            self.link_dr_last = link_last.dr
        if link_last.da is not None:
            self.link_da_last = link_last.da

    # @link_price_avg.expression
    # def link_price_avg(cls):
    #     return sa.select(sa.func.avg(LinkModel.price).label('average')).filter(LinkModel.page_url_domain_id == cls.id)

    @hybrid_property
    def tags_id(self):
        return [tag.id for tag in self.tags]

    @tags_id.expression
    def tags_id(cls):
        return sa.select(PageUrlDomainTagAssociation.tag_id) \
            .filter(PageUrlDomainTagAssociation.page_url_domain_id == cls.id)

    @hybrid_property
    def language_tags(self):
        language_tags = []
        if self.tags:
            language_tags = [tag for tag in self.tags if tag.ref_property == 'language']
        return language_tags

    @language_tags.expression
    def language_tags(cls):
        return sa.select(TagModel).select_from(TagModel).join(cls.tags) \
            .filter(TagModel.ref_property == 'language')

    @hybrid_property
    def language_tags_id(self):
        return [tag.id for tag in self.tags if tag.ref_property == 'language']

    @language_tags_id.expression
    def language_tags_id(cls):
        return sa.select(sa.distinct(TagModel.id)).select_from(TagModel).join(cls.tags) \
            .filter(TagModel.ref_property == 'language')

    @hybrid_property
    def country_tags(self):
        country_tags = []
        if self.tags:
            country_tags = [tag for tag in self.tags if tag.ref_property == 'country']
        return country_tags

    @country_tags.expression
    def country_tags(cls):
        return sa.select(TagModel).select_from(TagModel).join(cls.tags) \
            .filter(TagModel.ref_property == 'country')

    @hybrid_property
    def country_tags_id(self):
        return [tag.id for tag in self.tags if tag.ref_property == 'country']

    @country_tags_id.expression
    def country_tags_id(cls):
        return sa.select(sa.distinct(TagModel.id)).select_from(TagModel).join(cls.tags) \
            .filter(TagModel.ref_property == 'country')

    def __repr__(self):
        return f"<PageUrlDomainModel> (id={self.id}, name={self.name})"
