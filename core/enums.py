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
    sent_to_webmaster = 'sent to webmaster'
    closed = 'closed'

    def __str__(self):
        return self.value


class EnvEnum(str, Enum):
    local = 'local'
    docker_compose_local = 'docker-compose-local'
    prod = 'prod'


class UTCTimeZonesEnum(str, Enum):
    utc_p14 = "UTC+14"
    utc_p13 = "UTC+13"
    utc_p12 = "UTC+12"
    utc_p11 = "UTC+11"
    utc_p10 = "UTC+10"
    utc_p09 = "UTC+9"
    utc_p08 = "UTC+8"
    utc_p07 = "UTC+7"
    utc_p06 = "UTC+6"
    utc_p05 = "UTC+5"
    utc_p04 = "UTC+4"
    utc_p03 = "UTC+3"
    utc_p02 = "UTC+2"
    utc_p01 = "UTC+1"
    utc_p00 = "UTC+0"
    utc_m01 = "UTC−1"
    utc_m02 = "UTC−2"
    utc_m03 = "UTC−3"
    utc_m04 = "UTC−4"
    utc_m05 = "UTC−5"
    utc_m06 = "UTC−6"
    utc_m07 = "UTC−7"
    utc_m08 = "UTC−8"
    utc_m09 = "UTC−9"
    utc_m10 = "UTC−10"
    utc_m11 = "UTC−11"
    utc_m12 = "UTC−12"
