from datetime import datetime

from sqlalchemy import types


def init_models():
    from database.models import link, link_check, link_url_domain, page_url_domain, user


class FormattedDateTime(types.TypeDecorator):
    impl = types.DateTime

    cache_ok = True

    def process_result_value(self, value: datetime, dialect):
        if value is None:
            return None

        return value.strftime("%d.%m.%Y %H:%M")
