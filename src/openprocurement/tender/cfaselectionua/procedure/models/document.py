from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.types import HashType
from openprocurement.tender.core.procedure.models.document import BaseDocument


class ContractDocument(BaseDocument):
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    dateModified = StringType()
    author = StringType()
