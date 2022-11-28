from typing import Type
import fastapi as fa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from database import Base
from database.models.link import LinkModel
from database.models.user import UserModel
from database.schemas.link import LinkCreateWithDomainsSerializer
from database.schemas.user import UserCreateSerializer


def get(db: Session, Model: Type[Base], **kwargs) -> Base:
    return db.query(Model).filter_by(**kwargs).first()


def get_query_all_active(db: Session, Model: Type[Base], **kwargs) -> Query:
    return db.query(Model).filter_by(is_active=True, **kwargs)


def get_query_all_inactive(db: Session, Model: Type[Base], **kwargs) -> Query:
    return db.query(Model).filter_by(is_active=False, **kwargs)


def create(db: Session, Model: Type[Base], serializer) -> Base:
    serializer_data = jsonable_encoder(serializer)
    model_obj = Model(**serializer_data)
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj


def get_or_create_many(db: Session, Model: Type[Base], serializers: list[BaseModel]) -> list[Base]:
    obj_list = []
    for serializer in serializers:
        serializer_data = jsonable_encoder(serializer)
        model_obj = db.query(Model).filter_by(**serializer_data).first()
        if not model_obj:
            model_obj = Model(**serializer_data)
            db.add(model_obj)
        obj_list.append(model_obj)
    db.commit()
    return obj_list


def get_or_create_many_links_from_archive(db: Session, link_create_ser_list: list[LinkCreateWithDomainsSerializer]) -> list[Base]:
    links = []
    for link_ser in link_create_ser_list:
        link_ser_data = jsonable_encoder(link_ser)
        link = db.query(LinkModel).filter_by(
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
            link = LinkModel(**link_ser_data)
            db.add(link)

        links.append(link)

    db.commit()
    return links


def create_many(db: Session, Model: Type[Base], serializers: list[BaseModel]) -> list[Base]:
    obj_list = []
    for serializer in serializers:
        serializer_data = jsonable_encoder(serializer)
        model_obj = Model(**serializer_data)
        db.add(model_obj)
        obj_list.append(model_obj)
    db.commit()
    return obj_list


def get_or_create(db: Session, Model: Type[Base], serializer: BaseModel) -> Base:
    serializer_data = jsonable_encoder(serializer)
    model_obj = db.query(Model).filter_by(**serializer_data).first()
    if not model_obj:
        model_obj = Model(**serializer_data)
        db.add(model_obj)
        db.commit()
        db.refresh(model_obj)
    return model_obj


def get_or_create_by_name(session: Session, Model: Type[Base], name: str) -> (Base, bool):
    created = False
    model_obj = session.query(Model).filter_by(name=name).first()
    if model_obj is None:
        model_obj = Model(name=name)
        session.add(model_obj)
        session.commit()
        session.refresh(model_obj)
        created = True
    return model_obj, created


def update(db: Session, model_obj: Base, serializer: BaseModel | dict) -> Base:
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
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj


def remove(db: Session, Model: Type[Base], id: int) -> None:
    model_obj = db.query(Model).get(id)
    if model_obj is None:
        raise fa.HTTPException(status_code=404, detail=f"Trying to remove {Model} with id {id}, which is not found.")
    db.delete(model_obj)
    db.commit()


def create_user_from_keycloak(db, kc_admin, user_email, user_first_name, user_last_name) -> UserModel:
    user_ser = UserCreateSerializer(email=user_email, first_name=user_first_name, last_name=user_last_name,
                                    is_active=False)
    kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    if not kc_user_uuid:
        kc_admin.create_user(user_ser)
        kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    user_ser.uuid = kc_user_uuid

    user = create(db, UserModel, user_ser)
    return user
