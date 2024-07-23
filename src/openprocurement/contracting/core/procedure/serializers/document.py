from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.document import ConfidentialityTypes
from openprocurement.api.procedure.serializers.document import (
    DocumentSerializer as BaseDocumentSerializer,
)
from openprocurement.contracting.core.procedure.utils import is_tender_owner


class DocumentSerializer(BaseDocumentSerializer):
    def __init__(self, data: dict):
        self.private_fields = set()
        super().__init__(data)
        if data.get("confidentiality", "") == ConfidentialityTypes.BUYER_ONLY:
            request = get_request()
            if not is_tender_owner(request, request.validated["contract"]):
                self.private_fields.add("url")


class ContractDocumentSerializer(DocumentSerializer):
    serializers = {}
