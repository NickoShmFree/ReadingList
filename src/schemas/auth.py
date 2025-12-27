from pydantic import BaseModel, EmailStr


class VerifyEmailRequest(BaseModel):
    token: str


class JWTPayloadRefresh(BaseModel):
    sub: str


class JWTPayloadAccess(JWTPayloadRefresh):
    display_name: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
