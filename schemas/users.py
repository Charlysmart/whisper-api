from enum import Enum
from pydantic import BaseModel, EmailStr, model_validator


class FetchIn(str, Enum):
    single = "single"
    all = "all"


class RegisterUserIn(BaseModel):
    username : str
    email : EmailStr
    password : str
    confirm_password : str

    @model_validator(mode='after')
    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match!")
        return self
    

class LoginInfo(BaseModel):
    username : str
    password : str