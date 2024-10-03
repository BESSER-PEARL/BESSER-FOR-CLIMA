from pydantic import BaseModel, Field#, EmailStr


class TokenSchema(BaseModel):
    access_token: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "Your access token."
                }
        }

class UserSchema(BaseModel):
    fullname: str = Field(...)
    # email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "Max Mustermann",
                "email": "max.mustermann@gmail.com",
                "password": "weakpassword"
            }
        }

class UserLoginSchema(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "max.mustermann@gmail.com",
                "password": "weakpassword"
            }
        }
