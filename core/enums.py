from enum import Enum


class OrderEnum(Enum):
    asc = 'asc'
    desc = 'desc'


class UserOrderByEnum(Enum):
    id = 'id'
    created_at = 'created_at'


class LinkCheckOrderByEnum(Enum):
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


class LinkStatusEnum(Enum):
    green = 'green'
    red = 'red'
    yellow = 'yellow'

    def __str__(self):
        return self.value
