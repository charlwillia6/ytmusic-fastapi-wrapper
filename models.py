from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class CredentialsModel(BaseModel):
    id: int
    token: str
    refresh_token: Optional[str]
    token_uri: str
    client_id: str
    client_secret: str
    scopes: Optional[List[str]]

    model_config = ConfigDict(from_attributes=True)
