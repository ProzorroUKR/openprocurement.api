from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.framework.cfaua.procedure.utils import convert_agreement_type
from openprocurement.framework.core.procedure.serializers.contract import (
    ContractSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class AgreementSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "tender_token",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_modified",
        "public_ts",
        "is_public",
        "is_test",
        "config",
        "attachments",
        "date",
        "dateCreated",
    }

    serializers = {
        "agreementType": convert_agreement_type,
        "documents": ListSerializer(DocumentSerializer),
        "contracts": ListSerializer(ContractSerializer),
        "changes": ListSerializer(BaseSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
