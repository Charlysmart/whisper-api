from pydantic import BaseModel, model_validator
from enum import Enum


class Filter(str, Enum):
    all = "all"
    unread = "unread"
    replied = "replied"

class AnonymousIn(BaseModel):
    username : str
    content : str
    be_replied : bool

    @model_validator(mode="after")
    def anonymous_setting(self):
        self.username = self.username.lower().strip()
        return self


class ChatIn(BaseModel):
    message : str
    image : str
    message_thread : str