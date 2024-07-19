from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class ContractDocumentSerializer(DocumentSerializer):
    serializers = {}


class ContractBaseSerializer(BaseUIDSerializer):
    private_fields = {
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "tender_token",
        "owner_token",
        "bid_owner",
        "bid_token",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
        "config",
    }
    serializers = {
        "documents": ListSerializer(ContractDocumentSerializer),
    }
