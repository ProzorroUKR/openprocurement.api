from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.document import (
    DocumentSerializer as BaseDocumentSerializer,
)
from openprocurement.contracting.core.procedure.utils import (
    is_confidential_document_allowed,
)


class DocumentSerializer(BaseDocumentSerializer):
    def __init__(self, data: dict):
        self.private_fields = set()
        super().__init__(data)
        if not is_confidential_document_allowed(get_request(), data):
            self.private_fields.add("url")


class ContractDocumentSerializer(DocumentSerializer):
    serializers = {}
