import abc
from typing import Type

import fastapi as fa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm.query import Query

from database import Base
from database.models.content_data_dashboard import ContentDataModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.task import TaskContentModel
from database.models.user import UserModel
from database.schemas.content_data_dashboard import ContentDataCreateSerializer


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

    def get(self, Model, **kwargs) -> Base:
        model_obj = self.session.query(Model).filter_by(**kwargs).first()
        if model_obj is None:
            raise fa.HTTPException(status_code=404, detail=f"{Model} not found")
        return model_obj

    def get_many(self, Model, **kwargs):
        model_obj_list = self.session.query(Model).filter_by(**kwargs).all()
        return model_obj_list

    def get_many_by_id(self, Model, id_list):
        """getting objs one by one and if cant find any of them, raises 404"""
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

    def get_query(self, Model, **kwargs) -> Query:
        query = self.session.query(Model)
        for attr, value in kwargs.items():
            query = query.filter(Model.__dict__.get(attr) == value)
        return query

    def get_query_all_active(self, Model, **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=True, **kwargs)

    def get_query_all_inactive(self, Model, **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=False, **kwargs)

    def get_or_create(self, Model, serializer: BaseModel):
        serializer_data = jsonable_encoder(serializer)
        is_created = False
        model_obj = self.session.query(Model).filter_by(**serializer_data).first()
        if not model_obj:
            model_obj = Model(**serializer_data)
            self.session.add(model_obj)
            self.session.commit()
            self.session.refresh(model_obj)
            is_created = True
        return is_created, model_obj

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

    def get_or_create_by_kwargs(self, Model: Type[Base], **kwargs) -> tuple[bool, Base]:
        is_created = False
        model_obj = self.session.query(Model).filter_by(**kwargs).first()
        if not model_obj:
            model_obj = Model(**kwargs)
            self.session.add(model_obj)
            self.session.commit()
            self.session.refresh(model_obj)
            is_created = True
        return is_created, model_obj

    def update(self, model_obj: Base, serializer: BaseModel | dict) -> Base:
        """bug of fastapi.encoders.jsonable_encoder with sqlalchemy.ext.hybrid.hybrid_property,
        that's why we should cut leading '_' in model_obj_data_field"""
        model_obj_data = jsonable_encoder(model_obj)
        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.dict(exclude_unset=True)

        # when content_author is being set to task, should check if content_data created for task
        if isinstance(model_obj, TaskContentModel):
            if model_obj.content_author_id is None and update_data.get('content_author_id') is not None:
                model_obj.content_author_id = update_data['content_author_id']
                self.get_or_create_content_data_for_tasks([model_obj])

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

    def check_if_user_already_registered(self, user_ser) -> None:
        """checks if user with the same email as user_ser.email already exists"""
        user_with_the_same_email = self.session.query(UserModel) \
            .filter_by(email=user_ser.email).first()
        if user_with_the_same_email is not None:
            raise fa.HTTPException(status_code=400, detail="Email already registered")

    def update_users_seo_link_url_domains(self, user: UserModel,
                                          seo_link_url_domains_id: list[int]) -> UserModel:
        seo_link_url_domains = self.session.query(LinkUrlDomainModel) \
            .where(LinkUrlDomainModel.id.in_(seo_link_url_domains_id)).all()
        user.seo_link_url_domains = seo_link_url_domains
        self.session.commit()
        self.session.refresh(user)
        return user

    def deactivate_user(self, user) -> None:
        if not user.is_active:
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                   detail='This user is inactive already')
        user.is_active = False
        self.session.commit()

    def activate_user(self, user) -> None:
        if user.is_active:
            raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                                   detail='This user is active already')
        user.is_active = True
        self.session.commit()

    def get_or_create_content_data_for_tasks(self, tasks: list[TaskContentModel]) -> list[str]:
        results = []
        for task in tasks:
            try:
                create_ser = ContentDataCreateSerializer(content_author_id=task.content_author_id,
                                                         year=task.created_at.year,
                                                         month=task.created_at.month)
                is_created, content_data = self.get_or_create_by_kwargs(ContentDataModel,
                                                                        content_author_id=create_ser.content_author_id,
                                                                        year=create_ser.year,
                                                                        month=create_ser.month)
                if not is_created:
                    results.append(f'content_data for {task.id=:} already created: {content_data=:}')
            except fa.exceptions.ValidationError as e:
                results.append(str(e))
        return results

    def check_if_content_data_created_on_tasks_all(self) -> list[str]:
        tasks = self.get_all(TaskContentModel)
        return self.get_or_create_content_data_for_tasks(tasks)

    def check_if_content_data_created_on_tasks_by_ids(self, id_list: list[int]) -> list[str]:
        tasks = self.get_many_by_id(TaskContentModel, id_list=id_list)
        return self.get_or_create_content_data_for_tasks(tasks)
