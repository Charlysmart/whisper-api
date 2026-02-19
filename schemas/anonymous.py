from pydantic import BaseModel

class AnonymousIn(BaseModel):
    username : str
    message : str
    be_replied : bool


class ChatIn(BaseModel):
    message : str
    image : str
    message_thread : str