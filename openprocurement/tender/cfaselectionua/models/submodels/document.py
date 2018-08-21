from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from openprocurement.tender.core.models import Document


class AgreementDocument(Document):
    class Options:
        namespace = 'document'
        roles = RolesFromCsv('Document.csv', relative_to=__file__)

    language = StringType(required=True, choices=['uk', 'en', 'ru'], default='uk')
