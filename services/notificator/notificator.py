import logging
import smtplib
import traceback
from email.message import EmailMessage

import requests
from sqlalchemy.orm import Session

from core.config import settings
from database.models.link import LinkModel
from database.models.link_check import LinkCheckModel
from database.models.user import UserModel

logger = logging.getLogger(name='notificator')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/notificator/notificator.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

SSL_EXPIRATION_DAYS = 30


def prepare_message_count_status(db: Session, user: UserModel):
    # You have 100 links:
    # red: 80 pcs.
    # green: 20 pcs.
    user_links_qty = db.query(LinkModel.id).filter(LinkModel.user_id == user.id) \
        .count()
    linkchecks_red_qty = db.query(LinkModel.id).filter(LinkModel.user_id == user.id) \
        .filter(LinkModel.link_check_last_status == 'red') \
        .count()
    linkchecks_green_qty = db.query(LinkModel.id).filter(LinkModel.user_id == user.id) \
        .filter(LinkModel.link_check_last_status == 'green') \
        .count()
    message = f"You have {user_links_qty} links:\n" \
              f"red: {linkchecks_red_qty} pcs.\n" \
              f"green: {linkchecks_green_qty} pcs.\n\n"
    return message


def prepare_message_count_status_head(db: Session):
    """
    returns the following text:
    "TOTAL IN SYSTEM WE HAVE 16134 links:
    red: 3854 pcs.
    green: 12280 pcs."
    """
    links = db.query(LinkModel.id).count()
    linkchecks_red = db.query(LinkModel.id).where(LinkModel.link_check_last_status == 'red').count()
    linkchecks_green = db.query(LinkModel.id).where(LinkModel.link_check_last_status == 'green').count()
    message = f"TOTAL IN SYSTEM WE HAVE {links} links:\n" \
              f"red: {linkchecks_red} pcs.\n" \
              f"green: {linkchecks_green} pcs.\n\n"
    return message


def prepare_message_count_status_teamlead(db: Session, user: UserModel):
    """
    returns the following text:
    "TOTAL YOUR TEAM HAS 16134 links:
    red: 3854 pcs.
    green: 12280 pcs."
    """
    linkbuilders_id_list = [linkbuilder.id for linkbuilder in user.linkbuilders]
    links = db.query(LinkModel).filter(LinkModel.user_id.in_(linkbuilders_id_list)).all()
    linkchecks_red = db.query(LinkModel).where(LinkModel.link_check_last_status == 'red').all()
    linkchecks_green = db.query(LinkModel).where(LinkModel.link_check_last_status == 'green').all()
    message = f"TOTAL YOUR TEAM HAS {len(links)} links:\n" \
              f"red: {len(linkchecks_red)} pcs.\n" \
              f"green: {len(linkchecks_green)} pcs.\n\n"
    return message


def prepare_message_ssl_expiration_head(db: Session, expires_in_days) -> str:
    """
    returns the following text:
    "TOTAL IN SYSTEM SSL expiry issues:
    1134 links expire in 30 days and less."
    """
    links_expires_soon_qty = db.query(LinkModel.id) \
        .join(LinkCheckModel, LinkModel.link_check_last_id == LinkCheckModel.id) \
        .filter(LinkCheckModel.ssl_expires_in_days <= expires_in_days) \
        .count()
    message = ""
    if links_expires_soon_qty > 0:
        message = f"TOTAL IN SYSTEM SSL expiry issues:\n" \
                  f"{links_expires_soon_qty} links expire in {expires_in_days} days and less.\n\n"
    return message


def prepare_message_ssl_expiration_teamlead(db: Session, user: UserModel, expires_in_days) -> str:
    """
    returns the following text:
    "TOTAL YOUR TEAM SSL expiry issues:
    1134 links expire in 30 days and less."
    """
    linkbuilders_id_list = [linkbuilder.id for linkbuilder in user.linkbuilders]
    links_expires_soon_qty = db.query(LinkModel.id) \
        .join(LinkCheckModel, LinkModel.link_check_last_id == LinkCheckModel.id) \
        .filter(LinkCheckModel.ssl_expires_in_days <= expires_in_days) \
        .filter(LinkModel.user_id.in_(linkbuilders_id_list)) \
        .count()
    message = ""
    if links_expires_soon_qty > 0:
        message = f"TOTAL YOUR TEAM SSL expiry issues:\n" \
                  f"{links_expires_soon_qty} links expire in {expires_in_days} days and less.\n\n"
    return message


def prepare_message_ssl_expiration_linkbuilder(db: Session, user: UserModel, expires_in_days) -> str:
    """
    returns the following text:
    "You have SSL expiry issues:
    1134 links expire in 30 days and less."
    """
    links_expires_soon_qty = db.query(LinkModel.id) \
        .join(LinkCheckModel, LinkModel.link_check_last_id == LinkCheckModel.id) \
        .filter(LinkCheckModel.ssl_expires_in_days <= expires_in_days) \
        .filter(LinkModel.user_id == user.id) \
        .count()
    message = ""
    if links_expires_soon_qty > 0:
        message = f"You have SSL expiry issues:\n" \
                  f"{links_expires_soon_qty} links expire in {expires_in_days} days and less.\n\n"
    return message


def send_telegram(user: UserModel, message: str) -> None:
    """sends message to user.telegram_id using telegram api"""
    try:
        data = {"chat_id": user.telegram_id, "text": message}
        requests.post(
            "https://api.telegram.org/bot746467909:AAHxI9VDVPWEA8Oe_IE9e67r3C6oi7631_4/sendMessage",
            data=data)
        logger.info(f"Successfully sent telegram to {user}.")
    except Exception:
        logger.error(traceback.format_exc())


def send_email(user: UserModel, message):
    """sends email to user.email using settings.SMTP"""
    msg = EmailMessage()
    msg['Subject'] = "report.kaisaco.com"
    msg['From'] = settings.EMAILS_FROM_EMAIL
    msg['To'] = user.email
    msg.set_content(
        f"{message}\n\n"
        f"This message was sent automatically, you don't  need to reply to it.\n"
        f"To cancel receiving report emails - visit report.kaisaco.com and turn off notifications."
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.send_message(msg)
            logger.info(f"Successfully sent email to {user}.")
    except Exception:
        logger.error(traceback.format_exc())


def notify_user(db: Session, user: UserModel):
    """
    notifies user to telegram and email with message about red/green links and their ssl issues
    """
    message = f'{user.first_name}, hi!\n'

    if user.is_head:
        message += prepare_message_count_status_head(db)
        message += prepare_message_ssl_expiration_head(db, SSL_EXPIRATION_DAYS)

    if user.is_teamlead:
        message += prepare_message_count_status_teamlead(db, user)
        message += prepare_message_ssl_expiration_teamlead(db, user, SSL_EXPIRATION_DAYS)

    message += prepare_message_count_status(db, user)
    message += prepare_message_ssl_expiration_linkbuilder(db, user, SSL_EXPIRATION_DAYS)
    message += "More information at report.kaisaco.com."
    if user.is_accepting_telegram and user.telegram_id:
        send_telegram(user, message)
    else:
        logger.warning(f'Cant send telegram message to {user}, '
                       f'user.telegram_id: {user.telegram_id}, '
                       f'user.is_accepting_telegram: {user.is_accepting_telegram}')

    if user.is_accepting_emails:
        send_email(user, message)
    else:
        logger.warning(f"Can't send email to {user}, "
                       f"user.is_accepting_emails: {user.is_accepting_emails}")


def notify_users(db: Session, users: list[UserModel]):
    for user in users:
        notify_user(db, user)
