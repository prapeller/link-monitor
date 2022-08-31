from pydantic import BaseModel


class AccessTokenSerializer(BaseModel):
    access_token: str | None = None
    expires_in: int | None = None
    refresh_expires_in: int | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    session_state: str | None = None
    scope: str | None = None
