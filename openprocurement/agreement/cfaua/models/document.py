from schematics.types import StringType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import Document as BaseDocument


class Document(BaseDocument):

    documentOf = StringType(
        required=True,
        choices=['tender', 'item', 'contract', 'agreement']
    )