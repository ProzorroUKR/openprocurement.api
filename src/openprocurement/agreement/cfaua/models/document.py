from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from openprocurement.api.models import Document as BaseDocument


class Document(BaseDocument):
    class Options:
        roles = RolesFromCsv('Document.csv', relative_to=__file__)

    documentOf = StringType(
        required=True,
        choices=['tender', 'item', 'contract', 'agreement', 'lot', 'change'],
        default='agreement'
    )
