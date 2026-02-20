from pydantic import BaseModel

class SettingIn(BaseModel):
    email : bool
    push : bool