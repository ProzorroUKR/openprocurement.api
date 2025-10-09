from nacl.signing import SigningKey, VerifyKey
from pydantic import HttpUrl

from openprocurement.api.models_async.common import BaseModel


class DocStorageConfig(BaseModel):
    service_url: str
    dep_service_url: str | None
    username: str
    password: str
    upload_url: HttpUrl

    service_key: SigningKey
    keyring: dict[str, VerifyKey]
