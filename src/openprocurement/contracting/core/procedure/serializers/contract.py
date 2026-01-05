from datetime import datetime

from openprocurement.api.constants import (
    RATIONALE_TYPES_DECREE_1178,
    RATIONALE_TYPES_LAW_922,
    TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178,
    TZ,
)
from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)

DATE_BEFORE_TYPES_SPLITTING = TZ.localize(datetime(year=2022, month=10, day=12))


def get_change_rationale_types(tender):
    date_created = datetime.fromisoformat(tender["dateCreated"])
    if date_created < DATE_BEFORE_TYPES_SPLITTING:
        return RATIONALE_TYPES_LAW_922
    elif tender["procurementMethodType"] in TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178:
        return RATIONALE_TYPES_DECREE_1178
    else:
        return RATIONALE_TYPES_LAW_922


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

    def __init__(self, data: dict, tender=None, **kwargs):
        super().__init__(data, tender=tender, **kwargs)

        if tender and not data.get("contractChangeRationaleTypes"):
            data["contractChangeRationaleTypes"] = get_change_rationale_types(tender)
