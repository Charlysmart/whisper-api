from enum import Enum
from pydantic import BaseModel


class FetchIn(str, Enum):
    single = "single"
    all = "all"

class RoomIn(BaseModel):
    title : str
    display_admin : bool

class JoinRoomIn(BaseModel):
    thread : str