from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)


class ContractBaseSerializer(BaseUIDSerializer):
    private_fields = {
        "transfer_token",
        "doc_type",
        "rev",
        "tender_token",
        "owner_token",
        "bid_owner",
        "bid_token",
        "access",
        "revisions",
        "public_ts",
        "is_public",
        "is_test",
        "config",
    }
    optional_fields = {
        "public_modified",
    }
    serializers = {
        "documents": ListSerializer(ContractDocumentSerializer),
    }
