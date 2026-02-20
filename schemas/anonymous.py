from pydantic import BaseModel
from enum import Enum


class Filter(str, Enum):
    all = "all"
    unread = "unread"
    replied = "replied"

class AnonymousIn(BaseModel):
    username : str
    message : str
    be_replied : bool


class ChatIn(BaseModel):
    message : str
    image : str
    message_thread : str