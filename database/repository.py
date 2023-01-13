import abc
from typing import Type

import fastapi as fa
import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm.query import Query

from database import Base
from database.models.link import Link
from database.models.user import UserModel
from database.schemas.link import LinkCreateWithDomainsSerializer
from database.schemas.user import UserCreateSerializer


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, Model, serializer):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, Model, **kwargs) -> Base:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def create(self, Model, serializer):
        serializer_data = jsonable_encoder(serializer)
        model_obj = Model(**serializer_data)
        self.session.add(model_obj)
        self.session.commit()
        self.session.refresh(model_obj)
        return model_obj

    def get(self, Model, **kwargs):
        model_obj = self.session.query(Model).filter_by(**kwargs).first()
        if model_obj is None:
            raise fa.HTTPException(status_code=404, detail=f"{Model} not found")
        return model_obj

    def get_many(self, Model, **kwargs):
        model_obj_list = self.session.query(Model).filter_by(**kwargs).all()
        return model_obj_list

    def get_many_by_id(self, Model, id_list):
        model_obj_list = []
        for id in id_list:
            model_obj = self.session.query(Model).get(id)
            if model_obj is None:
                raise fa.HTTPException(status_code=404,
                                       detail=f"Trying to get {Model} with id {id}, which is not found.")
            model_obj_list.append(model_obj)
        return model_obj_list

    def get_all(self, Model):
        return self.session.query(Model).all()

    def get_all_active(self, Model):
        return self.session.query(Model).filter(Model.is_active == True).all()

    def get_all_inactive(self, Model):
        return self.session.query(Model).filter(Model.is_active == False).all()

    def get_query_all_active(self, Model, **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=True, **kwargs)

    def get_all_active_ordered_limited_offset(self, Model, order, order_by, limit, offset) -> Query:
        order = sa.desc if order == 'desc' else sa.asc
        return self.session.query(Model).filter_by(is_active=True).order_by(order(sa.text(order_by.value))).offset(
            offset).limit(limit).all()

    def get_all_inactive_ordered_limited_offset(self, Model, order, order_by, limit, offset) -> Query:
        order = sa.desc if order == 'desc' else sa.asc
        return self.session.query(Model).filter_by(is_active=False).order_by(order(sa.text(order_by.value))).offset(
            offset).limit(limit).all()

    def get_query_all_inactive(self, Model, **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=False, **kwargs)

    def get_or_create(self, Model, serializer: BaseModel):
        serializer_data = jsonable_encoder(serializer)
        model_obj = self.session.query(Model).filter_by(**serializer_data).first()
        if not model_obj:
            model_obj = Model(**serializer_data)
            self.session.add(model_obj)
            self.session.commit()
            self.session.refresh(model_obj)
        return model_obj

    def create_many(self, Model, serializers: list[BaseModel]):
        model_obj_list = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            model_obj = Model(**serializer_data)
            self.session.add(model_obj)
            model_obj_list.append(model_obj)
        self.session.commit()
        return model_obj_list

    def get_or_create_many(self, Model, serializers: list[BaseModel]):
        model_obj_list = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            model_obj = self.session.query(Model).filter_by(**serializer_data).first()
            if model_obj is None:
                model_obj = Model(**serializer_data)
                self.session.add(model_obj)
            model_obj_list.append(model_obj)
        self.session.commit()
        return model_obj_list

    def get_or_create_by_name(self, Model: Type[Base], name: str) -> Base:
        model_obj = self.session.query(Model).filter_by(name=name).first()
        if not model_obj:
            model_obj = Model(name=name)
            self.session.add(model_obj)
            self.session.commit()
            self.session.refresh(model_obj)
        return model_obj

    def update(self, model_obj, serializer: BaseModel | dict):
        """bug of fastapi.encoders.jsonable_encoder with sqlalchemy.ext.hybrid.hybrid_property,
        that's why we should cut leading '_' in model_obj_data_field"""
        model_obj_data = jsonable_encoder(model_obj)
        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.dict(exclude_unset=True)
        for model_obj_data_field in model_obj_data:
            field = model_obj_data_field.strip('_')
            if field in update_data:
                setattr(model_obj, field, update_data[field])
        self.session.add(model_obj)
        self.session.commit()
        self.session.refresh(model_obj)
        return model_obj

    def remove(self, Model, id: int) -> None:
        model_obj = self.session.query(Model).get(id)
        if model_obj is None:
            raise fa.HTTPException(status_code=404,
                                   detail=f"Trying to remove {Model} with id {id}, which is not found.")
        self.session.delete(model_obj)
        self.session.commit()

    def get_or_create_many_links_from_archive(self, link_create_ser_list: list[LinkCreateWithDomainsSerializer]):
        links = []
        for link_ser in link_create_ser_list:
            link_ser_data = jsonable_encoder(link_ser)
            link = self.session.query(Link).filter_by(
                page_url=link_ser_data['page_url'],
                link_url=link_ser_data['link_url'],
                anchor=link_ser_data['anchor'],
            ).first()

            if link:
                link.created_at = link_ser_data['created_at']
                link.user_id = link_ser_data['user_id']
                link.da = link_ser_data['da']
                link.dr = link_ser_data['dr']
                link.price = link_ser_data['price']

            if link is None:
                link = Link()
                for field in link_ser_data:
                    link.field = link_ser_data[field]
                self.session.add(link)

            links.append(link)

        self.session.commit()
        return links

    def create_user_from_keycloak(self, kc_admin, user_email, user_first_name, user_last_name) -> None:
        user_ser = UserCreateSerializer(email=user_email, first_name=user_first_name, last_name=user_last_name,
                                        is_active=False)
        kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
        if not kc_user_uuid:
            kc_admin.create_user(user_ser)
            kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
        user_ser.uuid = kc_user_uuid

        self.create(UserModel, user_ser)
