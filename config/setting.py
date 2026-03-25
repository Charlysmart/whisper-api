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
    sendiapi : str
    sitename : str
    cloudinarysecret : str
    cloudinaryapi : str

    class Config:
        env_file = ".env"