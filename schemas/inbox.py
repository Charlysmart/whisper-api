from enum import Enum


class Filter(str, Enum):
    all = "all"
    unread = "unread"
    
class FetchIn(str, Enum):
    single = "single"
    all = "all"