import sqlalchemy as sa
from sqlalchemy.orm import Session

from core.config import settings
from database.models.link import LinkModel
from database.models.link_check import LinkCheckModel
from database.models.user import UserModel


def prepare_text_count_status(session: Session, user: UserModel):
    # You have 100 links:
    # red: 80 pcs.
    # green: 20 pcs.
    user_links_qty = session.query(LinkModel.id).filter(LinkModel.user_id == user.id) \
        .count()
    linkchecks_red_qty = session.query(LinkModel.id).filter(LinkModel.user_id == user.id) \
        .filter(LinkModel.link_check_last_status == 'red') \
        .count()
    linkchecks_green_qty = session.query(LinkModel.id).filter(LinkModel.user_id == user.id) \
        .filter(LinkModel.link_check_last_status == 'green') \
        .count()
    text = f"You have {user_links_qty} links:\n" \
           f"red: {linkchecks_red_qty} pcs.\n" \
           f"green: {linkchecks_green_qty} pcs.\n\n"
    return text


def prepare_text_count_status_head(session: Session):
    """
    returns the following text:
    "TOTAL IN SYSTEM WE HAVE 16134 links:
    red: 3854 pcs.
    green: 12280 pcs."
    """
    links = session.query(LinkModel.id).count()
    linkchecks_red = session.query(LinkModel.id).where(LinkModel.link_check_last_status == 'red').count()
    linkchecks_green = session.query(LinkModel.id).where(LinkModel.link_check_last_status == 'green').count()
    text = f"TOTAL IN SYSTEM WE HAVE {links} links:\n" \
           f"red: {linkchecks_red} pcs.\n" \
           f"green: {linkchecks_green} pcs.\n\n"
    return text


def prepare_text_count_status_teamlead(session: Session, user: UserModel):
    """
    returns the following text:
    "TOTAL YOUR TEAM HAS 16134 links:
    red: 3854 pcs.
    green: 12280 pcs."
    """
    linkbuilders_id_list = [linkbuilder.id for linkbuilder in user.linkbuilders]
    links = session.query(LinkModel).where(
        LinkModel.user_id.in_(linkbuilders_id_list)
    ).all()
    linkchecks_red = session.query(LinkModel).where(sa.and_(
        LinkModel.user_id.in_(linkbuilders_id_list),
        LinkModel.link_check_last_status == 'red',
    )).all()
    linkchecks_green = session.query(LinkModel).where(sa.and_(
        LinkModel.user_id.in_(linkbuilders_id_list),
        LinkModel.link_check_last_status == 'green',
    )).all()
    text = f"TOTAL YOUR TEAM HAS {len(links)} links:\n" \
           f"red: {len(linkchecks_red)} pcs.\n" \
           f"green: {len(linkchecks_green)} pcs.\n\n"
    return text


def prepare_text_ssl_expiration_head(session: Session, expires_in_days) -> str:
    """
    returns the following text:
    "TOTAL IN SYSTEM SSL expiry issues:
    1134 links expire in 30 days and less."
    """
    links_expires_soon_qty = session.query(LinkModel.id) \
        .join(LinkCheckModel, LinkModel.link_check_last_id == LinkCheckModel.id) \
        .filter(LinkCheckModel.ssl_expires_in_days <= expires_in_days) \
        .count()
    text = ""
    if links_expires_soon_qty > 0:
        text = f"TOTAL IN SYSTEM SSL expiry issues:\n" \
               f"{links_expires_soon_qty} links expire in {expires_in_days} days and less.\n\n"
    return text


def prepare_text_ssl_expiration_teamlead(session: Session, user: UserModel, expires_in_days) -> str:
    """
    returns the following text:
    "TOTAL YOUR TEAM SSL expiry issues:
    1134 links expire in 30 days and less."
    """
    linkbuilders_id_list = [linkbuilder.id for linkbuilder in user.linkbuilders]
    links_expires_soon_qty = session.query(LinkModel.id) \
        .join(LinkCheckModel, LinkModel.link_check_last_id == LinkCheckModel.id) \
        .filter(LinkCheckModel.ssl_expires_in_days <= expires_in_days) \
        .filter(LinkModel.user_id.in_(linkbuilders_id_list)) \
        .count()
    text = ""
    if links_expires_soon_qty > 0:
        text = f"TOTAL YOUR TEAM SSL expiry issues:\n" \
               f"{links_expires_soon_qty} links expire in {expires_in_days} days and less.\n\n"
    return text


def prepare_text_ssl_expiration_linkbuilder(session: Session, user: UserModel, expires_in_days) -> str:
    """
    returns the following text:
    "You have SSL expiry issues:
    1134 links expire in 30 days and less."
    """
    links_expires_soon_qty = session.query(LinkModel.id) \
        .join(LinkCheckModel, LinkModel.link_check_last_id == LinkCheckModel.id) \
        .filter(LinkCheckModel.ssl_expires_in_days <= expires_in_days) \
        .filter(LinkModel.user_id == user.id) \
        .count()
    text = ""
    if links_expires_soon_qty > 0:
        text = f"You have SSL expiry issues:\n" \
               f"{links_expires_soon_qty} links expire in {expires_in_days} days and less.\n\n"
    return text


def prepare_linker_report_daily_text(session, user):
    """prepare message for
    linker
    about daily report about red/green links and their ssl issues"""
    text = f'{user.first_name}, hi!\n'

    if user.is_head:
        text += prepare_text_count_status_head(session)
        text += prepare_text_ssl_expiration_head(session, settings.SSL_EXPIRATION_DAYS)

    if user.is_teamlead:
        text += prepare_text_count_status_teamlead(session, user)
        text += prepare_text_ssl_expiration_teamlead(session, user, settings.SSL_EXPIRATION_DAYS)

    text += prepare_text_count_status(session, user)
    text += prepare_text_ssl_expiration_linkbuilder(session, user, settings.SSL_EXPIRATION_DAYS)
    return text


def prepare_content_author_todo_text(user, tasks_qty):
    """prepare text for
     content authors's
     about number of tasks
     which are not seen yet
     which status is 'sent_to_author' (to do)
     """
    text = f'{user.first_name}, hi!\n' \
           f'You have {tasks_qty} new "To Do" tasks.'
    return text


def prepare_content_author_in_edit_text(user, tasks_qty):
    """prepare text for
    content authors
    about number of tasks
    which are not seen yet
    which status is 'In Edit
    """
    text = f'{user.first_name}, hi!\n' \
           f'You have {tasks_qty} tasks changed to "In Edit" status.'
    return text


def prepare_content_author_deadline_overdue_text(user, tasks_qty):
    """prepare  text for
    content authors
    about number of tasks
    which status is 'sent_to_author' (to do)
    which deadline date is less or equal to current date (overdued)
    """
    text = f'{user.first_name}, hi!\n' \
           f'You have {tasks_qty} tasks "To Do" that are overdue already.'
    return text


def prepare_content_author_teamlead_idle_text(user):
    """prepare  message for
    content authors
    about number of tasks
    which status is 'sent_to_author' (to do)
    which deadline date is less or equal to current date (overdued)
    """
    text = f'{user.first_name}, hi!\n' \
           f'You were not assigned new tasks during last {settings.DAYS_CONTENT_AUTHORS_TEAMLEADS_IDLE_TO_NOTIFY} days.'
    return text
