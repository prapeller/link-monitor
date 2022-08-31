from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from database.models.user import UserModel
from database.schemas.link import LinkCreateWithDomainsSerializer
from database.schemas.user import UserCreateSerializer


def get(db: Session, Model, **kwargs):
    return db.query(Model).filter_by(**kwargs).first()


def get_query_all_active(db: Session, Model, **kwargs) -> Query:
    return db.query(Model).filter_by(is_active=True, **kwargs)


def get_query_all_inactive(db: Session, Model, **kwargs) -> Query:
    return db.query(Model).filter_by(is_active=False, **kwargs)


def create(db: Session, Model, serializer: BaseModel):
    serializer_data = jsonable_encoder(serializer)
    model_obj = Model(**serializer_data)
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj


def get_or_create_many(db: Session, Model, serializers: list[BaseModel]):
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


def get_or_create_many_links_from_archive(db: Session, LinkModel,
                                          serializers: list[LinkCreateWithDomainsSerializer]):
    links = []
    for serializer in serializers:
        serializer_data = jsonable_encoder(serializer)
        link = db.query(LinkModel).filter_by(
            page_url=serializer_data['page_url'],
            link_url=serializer_data['link_url'],
            anchor=serializer_data['anchor'],
        ).first()

        if link:
            link.created_at = serializer_data['created_at']
            link.user_id = serializer_data['user_id']
            link.da = serializer_data['da']
            link.dr = serializer_data['dr']
            link.price = serializer_data['price']

        if link is None:
            link = LinkModel(**serializer_data)
            db.add(link)

        links.append(link)

    db.commit()
    return links


def create_many(db: Session, Model, serializers: list[BaseModel]):
    obj_list = []
    for serializer in serializers:
        serializer_data = jsonable_encoder(serializer)
        model_obj = Model(**serializer_data)
        db.add(model_obj)
        obj_list.append(model_obj)
    db.commit()
    return obj_list


def get_or_create(db: Session, Model, serializer: BaseModel):
    serializer_data = jsonable_encoder(serializer)
    model_obj = db.query(Model).filter_by(**serializer_data).first()
    if not model_obj:
        model_obj = Model(**serializer_data)
        db.add(model_obj)
        db.commit()
        db.refresh(model_obj)
    return model_obj


def update(db: Session, model_obj, serializer):
    model_obj_data = jsonable_encoder(model_obj)
    if isinstance(serializer, dict):
        update_data = serializer
    else:
        update_data = serializer.dict(exclude_unset=True)
    for field in model_obj_data:
        if field in update_data:
            setattr(model_obj, field, update_data[field])
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj


def remove(db: Session, Model, id: int):
    model_obj = db.query(Model).get(id)
    db.delete(model_obj)
    db.commit()


def create_user_from_keycloak(db, kc_admin, user_email, user_first_name, user_last_name):
    user_ser = UserCreateSerializer(email=user_email, first_name=user_first_name, last_name=user_last_name,
                                    is_active=False)
    kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    if not kc_user_uuid:
        kc_admin.create_user(user_ser)
        kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    user_ser.uuid = kc_user_uuid

    user = create(db, UserModel, user_ser)
    return user
