from openprocurement.framework.core.procedure.serializers.contract import ContractSerializer
from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer, ListSerializer


class AgreementSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
        "config",
        "frameworkDetails",
        "__parent__",
        "_attachments",
    }

    serializers = {
        "contracts": ListSerializer(ContractSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
