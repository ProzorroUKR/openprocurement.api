from nacl.signing import SigningKey, VerifyKey
from pydantic import BaseModel, ConfigDict, HttpUrl


class DocStorageConfig(BaseModel):
    service_url: str
    dep_service_url: str | None
    username: str
    password: str
    upload_url: HttpUrl

    service_key: SigningKey
    keyring: dict[str, VerifyKey]

    model_config = ConfigDict(arbitrary_types_allowed=True)
