from enum import Enum


class FetchIn(str, Enum):
    single = "single"
    all = "all"