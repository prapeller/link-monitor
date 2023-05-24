import re
from datetime import datetime

import pydantic as pd

from core.enums import TagRefpropertyEnum


class TagCreateSerializer(pd.BaseModel):
    name: str
    full_name: str | None
    ref_property: TagRefpropertyEnum

    @pd.validator('name')
    def name_max_length(cls, v):
        if len(v) > 3:
            raise ValueError('Tag length should not be longer than 3 characters.')
        v = re.sub(pattern=r"[^a-zA-Z]+", repl='', string=v)
        return v.upper()


class TagReadSerializer(TagCreateSerializer):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True
