# enums.py
from enum import Enum

class ViewType(Enum):
    TXT = 1
    IMG = 2

class ContentType(Enum):
    TXT = 'txt'
    IMG = 'img'

    @classmethod
    def from_value(cls, value):
        for item in cls:
            if item.value == value:
                return item
        return None