from sqlmodel import Field, SQLModel


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


# Model for setting a new password via token
class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
