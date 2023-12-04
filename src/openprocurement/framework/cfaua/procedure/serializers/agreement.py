from openprocurement.framework.core.procedure.serializers.contract import ContractSerializer
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, BaseUIDSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer


class AgreementSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "tender_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
        "config",
        "__parent__",
        "_attachments",
        "date",
        "dateCreated",
        "agreementType",
    }

    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "contracts": ListSerializer(ContractSerializer),
        "changes": ListSerializer(BaseSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
