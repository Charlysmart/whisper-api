from typing import List
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    databaseurl : str
    jwtsecretcode : str
    algorithm : str  
    origins : List[str] = []
    httponly : bool
    samesite: str
    secure : bool

    class Config:
        env_file = ".env"