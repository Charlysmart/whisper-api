from enum import Enum
from typing import Literal
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
    def validate_info(self):
        self.username = self.username.lower()
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match!")
        return self
    
class AdminRegister(BaseModel):
    username : str
    email : EmailStr
    role : Literal["admin"]
    password : str
    
    @model_validator(mode='after')
    def convert_username(self):
        self.username = self.username.lower()
        return self
    

class LoginInfo(BaseModel):
    username : str
    password : str

    @model_validator(mode="after")
    def convert_username(self):
        self.username = self.username.lower()
        return self