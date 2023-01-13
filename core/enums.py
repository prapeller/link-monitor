from enum import Enum


class StartModeEnum(str, Enum):
    httpx = 'httpx'
    playwright = 'playwright'


class OrderEnum(str, Enum):
    asc = 'asc'
    desc = 'desc'


class UserOrderByEnum(str, Enum):
    id = 'id'
    created_at = 'created_at'


class LinkCheckOrderByEnum(str, Enum):
    id = 'id'
    created_at = 'created_at'


class LinkOrderByEnum(str, Enum):
    id = 'id'
    user_id = 'user_id'
    link_url_domain_name = 'link_url_domain_name'
    page_url = 'page_url'
    link_url = 'link_url'
    anchor = 'anchor'
    da = 'da'
    dr = 'dr'
    price = 'price'
    screenshot_url = 'screenshot_url'
    contact = 'contact'
    created_at = 'created_at'
    link_check_last_status = 'link_check_last_status'
    link_check_last_result_message = 'link_check_last_result_message'
    link_check_last_created_at = 'link_check_last_created_at'

    def __str__(self):
        return self.value


class PUDomainOrderByEnum(str, Enum):
    name = 'name'
    link_da_last = 'link_da_last'
    link_dr_last = 'link_dr_last'
    link_created_at_last = 'link_created_at_last'
    link_price_avg = 'link_price_avg'

    def __str__(self):
        return self.value


class LinkStatusEnum(str, Enum):
    green = 'green'
    red = 'red'
    yellow = 'yellow'

    def __str__(self):
        return self.value


class TagRefpropertyEnum(str, Enum):
    language = 'language'
    country = 'country'

    def __str__(self):
        return self.value


class TaskContentStatusEnum(str, Enum):
    sent_to_teamlead = 'sent to teamlead'
    sent_to_author = 'sent to author'
    text_written = 'text written'
    in_edit = 'in edit'
    confirmed = 'confirmed'
    closed = 'closed'

    def __str__(self):
        return self.value
