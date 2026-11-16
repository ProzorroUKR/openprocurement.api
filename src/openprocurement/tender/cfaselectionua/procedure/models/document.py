from pydantic import Field

from openprocurement.api.procedure.types import (
    MD5,
    Hash,
)
from openprocurement.tender.core.procedure.models.document import BaseDocument


class CFASelectionContractDocument(BaseDocument):
    id: MD5
    datePublished: str
    hash: Hash | None = None
    title: str
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str
    dateModified: str | None = None
    author: str | None = None
