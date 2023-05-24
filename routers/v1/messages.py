import fastapi as fa
import sqlalchemy as sa
from sqlalchemy.orm import Session

from core.dependencies import (get_session_dependency, get_current_user_dependency, get_sqlalchemy_repo_dependency)
from core.exceptions import UnauthorizedException
from database.crud import create, get, update, remove
from database.models.message import MessageModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.message import MessageReadSerializer, MessageCreateSerializer

router = fa.APIRouter()


@router.get("/to-me",
            response_model=list[MessageReadSerializer]
            )
def messages_list_all_to_me(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get messages sent to current user
    """

    return repo.session.query(MessageModel) \
        .filter_by(to_user_id=current_user.id, is_notified=True) \
        .order_by(sa.desc(MessageModel.created_at)).all()


@router.get("/from-me",
            response_model=list[MessageReadSerializer]
            )
def messages_list_all_from_me(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get messages sent from current user
    """

    return repo.session.query(MessageModel) \
        .filter_by(from_user_id=current_user.id, is_notified=True) \
        .order_by(sa.desc(MessageModel.created_at)).all()


@router.get("/{message_id}",
            response_model=MessageReadSerializer
            )
def messages_read(
        message_id: int = fa.Path(...),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get message by id
    """
    message = repo.get(MessageModel, id=message_id)
    current_user_is_recepient_or_receiver = message.from_user_id == current_user.id \
                                            or message.to_user_id == current_user.id
    if not current_user.is_head or not current_user_is_recepient_or_receiver:
        raise UnauthorizedException

    return message


@router.post("/to-user",
             response_model=MessageReadSerializer
             )
def messages_send_my_to_user(
        message_ser: MessageCreateSerializer = fa.Body(...),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
):
    """
    create message from current user to someone
    """
    message_ser.from_user_id = current_user.id
    message = create(db, MessageModel, message_ser)
    return message


@router.put("/mark-read-many",
            response_model=list[MessageReadSerializer]
            )
def messages_update(
        message_id_list: list[int] = fa.Body(...),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
):
    """
    set to messages from message_id_list 'is_read'=True
    """
    messages = db.query(MessageModel).filter(MessageModel.id.in_(message_id_list)).all()
    for message in messages:
        if message is None:
            raise fa.HTTPException(status_code=404, detail="Message not found")
        if not current_user.is_head and message.from_user_id != current_user.id and message.to_user_id != current_user.id:
            raise UnauthorizedException

        message.is_read = True
    db.commit()
    return messages


@router.put("/{message_id}",
            response_model=MessageReadSerializer
            )
def messages_update(
        message_id: int = fa.Path(...),
        message_ser: MessageCreateSerializer = fa.Body(...),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
):
    """
    update message by id
    """
    message = get(db, MessageModel, id=message_id)
    if message is None:
        raise fa.HTTPException(status_code=404, detail="Message not found")
    if not current_user.is_head and message.from_user_id != current_user.id and message.to_user_id != current_user.id:
        raise UnauthorizedException

    message = update(db, message, message_ser)
    return message


@router.delete("/many")
async def messages_delete_many(
        message_id_list: list[int] = fa.Body(...),
        db: Session = fa.Depends(get_session_dependency),
):
    """
    delete many messages from id_list
    """
    for message_id in message_id_list:
        remove(db, MessageModel, message_id)
    return {'message': 'ok'}


@router.delete("/{message_id}")
async def messages_delete(
        message_id: int = fa.Path(...),
        db: Session = fa.Depends(get_session_dependency),
):
    """
    delete message
    """
    remove(db, MessageModel, message_id)
    return {'message': 'ok'}
