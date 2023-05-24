import datetime as dt
import logging
import smtplib
from email.message import EmailMessage

import pytz
import requests
import sqlalchemy as sa

from core.config import settings
from core.enums import TaskContentStatusEnum
from core.timezones import TIMEZONES_DICT
from database import SessionLocal
from database.models.message import MessageModel
from database.models.task import TaskContentModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.message import MessageCreateSerializer
from services.notificator.text_preparer import (
    prepare_linker_report_daily_text,
    prepare_content_author_todo_text,
    prepare_content_author_in_edit_text,
    prepare_content_author_deadline_overdue_text,
    prepare_content_author_teamlead_idle_text,
)

logger = logging.getLogger(name='notificator')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/notificator/notificator.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Notificator:

    def __init__(self):
        self.session = SessionLocal()
        self.repo = SqlAlchemyRepository(self.session)

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    @staticmethod
    def send_email(user: UserModel, text):
        if user.is_accepting_emails:
            text += "\nThis email was sent automatically, you don't need to reply to it.\n" \
                    "To cancel receiving emails - visit report.kaisaco.com and turn off email notifications."""
            msg = EmailMessage()
            msg['Subject'] = "report.kaisaco.com"
            msg['From'] = settings.EMAILS_FROM_EMAIL
            msg['To'] = user.email
            msg.set_content(text)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.send_message(msg)
            logger.info(f"Successfully sent email to {user}.")

        else:
            logger.warning(f"Can't send email to {user}, user.is_accepting_emails: {user.is_accepting_emails}")

    @staticmethod
    def send_telegram(user: UserModel, text: str) -> None:
        """sends message to user.telegram_id using telegram api"""

        if user.is_accepting_telegram and user.telegram_id:
            text += "\nMore information at report.kaisaco.com."
            data = {"chat_id": user.telegram_id, "text": text}
            requests.post(f"https://api.telegram.org/{settings.TG_BOT_ID}/sendMessage", data=data)
            logger.info(f"Successfully sent telegram to {user}.")

        else:
            logger.warning(f'Cant send telegram message to {user}, '
                           f'user.telegram_id: {user.telegram_id}, '
                           f'user.is_accepting_telegram: {user.is_accepting_telegram}')

    def send_message(self, user: UserModel, text: str) -> None:
        self.repo.create(MessageModel, MessageCreateSerializer(to_user_id=user.id, text=text, is_notified=True))

    def notify_messages_user(self, user: UserModel):
        for message in user.pending_messages:
            self.send_email(user, message.text)
            self.send_telegram(user, message.text)
            message.is_notified = True
            self.session.commit()

    def notify_messages_all_users(self):
        users = self.repo.get_all_active(UserModel)
        for user in users:
            self.notify_messages_user(user)

    def prepare_content_author_todo_message(self, user: UserModel, tasks_qty):
        text = prepare_content_author_todo_text(user, tasks_qty)
        self.repo.create(MessageModel, MessageCreateSerializer(to_user_id=user.id, text=text))

    def prepare_content_author_changed_to_edit_message(self, user: UserModel, tasks_qty):
        text = prepare_content_author_in_edit_text(user, tasks_qty)
        self.repo.create(MessageModel, MessageCreateSerializer(to_user_id=user.id, text=text))

    def prepare_content_author_deadline_overdue_message(self, user: UserModel, tasks_qty):
        text = prepare_content_author_deadline_overdue_text(user, tasks_qty)
        self.repo.create(MessageModel, MessageCreateSerializer(to_user_id=user.id, text=text))

    def prepare_content_author_teamlead_idle_message(self, user: UserModel):
        text = prepare_content_author_teamlead_idle_text(user)
        self.repo.create(MessageModel, MessageCreateSerializer(to_user_id=user.id, text=text))

    def prepare_linker_report_daily_message(self, user: UserModel):
        text = prepare_linker_report_daily_text(self.session, user)
        self.repo.create(MessageModel, MessageCreateSerializer(to_user_id=user.id, text=text))

    def prepare_and_send_linkers_report_daily_messages(self):
        """if linker's current time is [settings.specified] - prepares and send (notifies about) message to him:
        -daily report
        """
        linkers = self.repo.get_query_all_active(UserModel) \
            .filter(sa.and_(
            UserModel.is_seo == False,
            UserModel.is_content_head == False,
            UserModel.is_content_teamlead == False,
            UserModel.is_content_author == False
        )).all()
        for user in linkers:
            user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[user.timezone]))
            if user_current_time.hour in settings.NOTIFICATIONS_HOURS_LINKERS_DAILY_REPORT:
                self.prepare_linker_report_daily_message(user)
                self.notify_messages_user(user)

    def prepare_and_send_content_author_todo_messages(self):
        """ if content_author's current time is [settings.specified] - prepares and send (notifies about) message to him
        -report about new to do tasks
        """
        content_authors = self.repo.get_query_all_active(UserModel) \
            .filter(UserModel.is_content_author == True).all()
        for user in content_authors:
            user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[user.timezone]))
            if user_current_time.hour in settings.NOTIFICATIONS_HOURS_CONTENT_AUTHORS_TODO:
                tasks_qty = self.session.query(TaskContentModel.id).filter(sa.and_(
                    TaskContentModel.content_author_id == user.id,
                    TaskContentModel.content_author_viewed is False,
                )).count()
                if tasks_qty > 0:
                    self.prepare_content_author_todo_message(user, tasks_qty)
                    self.notify_messages_user(user)

    def prepare_and_send_content_author_changed_to_edit_messages(self):
        """ if content_author's current time is [settings.specified] - prepares and send (notifies about) message to him
        -report about changed to 'in edit' status tasks
        """
        content_authors = self.repo.get_query_all_active(UserModel).filter(UserModel.is_content_author == True).all()
        for user in content_authors:
            user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[user.timezone]))
            if user_current_time.hour in settings.NOTIFICATIONS_HOURS_CONTENT_AUTHORS_INEDIT:
                tasks_qty = self.session.query(TaskContentModel.id).filter(sa.and_(
                    TaskContentModel.content_author_id == user.id,
                    TaskContentModel.status == TaskContentStatusEnum.in_edit,
                    TaskContentModel.content_author_viewed is False,
                )).count()
                if tasks_qty > 0:
                    self.prepare_content_author_changed_to_edit_message(user, tasks_qty)
                    self.notify_messages_user(user)

    def prepare_and_send_content_author_deadline_overdue_messages(self):
        """ if content_author's current time is [settings.specified] - prepares and send (notifies about) message to him
        -report about overdue 'to do' tasks
        """
        content_authors = self.repo.get_query_all_active(UserModel).filter(UserModel.is_content_author == True).all()
        for user in content_authors:
            user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[user.timezone]))
            if user_current_time.hour in settings.NOTIFICATIONS_HOURS_CONTENT_AUTHORS_TODO_OVERDUE:
                tasks_qty = self.session.query(TaskContentModel.id).filter(sa.and_(
                    TaskContentModel.content_author_id == user.id,
                    TaskContentModel.status != TaskContentStatusEnum.sent_to_author,
                    sa.cast(TaskContentModel.deadline_at, sa.Date) <= dt.datetime.now().date(),
                )).count()
                if tasks_qty > 0:
                    self.prepare_content_author_deadline_overdue_message(user, tasks_qty)
                    self.notify_messages_user(user)

    def prepare_and_send_content_author_and_teamlead_are_idle_messages(self):
        """ if content_author/content_teamlead current time is [settings.specified] - prepares and send (notifies about) message to him
        -report about they are overdue 'to do' tasks
        """
        content_authors_teamleads: list[UserModel] = self.repo.get_query_all_active(UserModel).filter(sa.or_(
            UserModel.is_content_author == True,
            UserModel.is_content_teamlead == True,
        )).all()
        for user in content_authors_teamleads:
            user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[user.timezone]))
            if user_current_time.hour in settings.NOTIFICATIONS_HOURS_CONTENT_AUTHORS_TEAMLEADS_IDLE:
                # for teamleads
                last_task = None
                if user.is_content_teamlead:
                    last_task = self.session.query(TaskContentModel).where(
                        TaskContentModel.content_teamlead_id == user.id,
                    ).order_by(sa.desc(TaskContentModel.id)).limit(1).first()
                # for authors
                if user.is_content_author:
                    last_task = self.session.query(TaskContentModel).where(
                        TaskContentModel.content_author_id == user.id,
                    ).order_by(sa.desc(TaskContentModel.id)).limit(1).first()

                if last_task is not None and last_task.created_at.date() < dt.datetime.today().date() - dt.timedelta(
                        days=settings.DAYS_CONTENT_AUTHORS_TEAMLEADS_IDLE_TO_NOTIFY):
                    self.prepare_content_author_teamlead_idle_message(user)
                    self.notify_messages_user(user)
