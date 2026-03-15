from pydantic import BaseModel, model_validator


class ResetPassword(BaseModel):
    password : str
    confirm_password : str

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match!")
        return self