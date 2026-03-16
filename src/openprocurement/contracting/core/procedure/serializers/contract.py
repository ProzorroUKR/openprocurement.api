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
from openprocurement.contracting.core.constants import (
    FROZEN_RATIONALE_TYPES_DECREE_1178,
    FROZEN_RATIONALE_TYPES_LAW_922,
)
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)

DATE_BEFORE_TYPES_SPLITTING = TZ.localize(datetime(year=2022, month=10, day=12))


def get_change_rationale_types_frozen(tender):
    # Old tenders use LAW922
    date_created = datetime.fromisoformat(tender["dateCreated"])
    if date_created < DATE_BEFORE_TYPES_SPLITTING:
        return FROZEN_RATIONALE_TYPES_LAW_922

    # New causeDetails.scheme logic
    cause_details = tender.get("causeDetails", {})
    cause_scheme = cause_details.get("scheme")
    if cause_scheme == "DECREE1178":
        return FROZEN_RATIONALE_TYPES_DECREE_1178
    if cause_scheme == "LAW922":
        return FROZEN_RATIONALE_TYPES_LAW_922

    # Some procurementMethodType use DECREE1178
    if tender["procurementMethodType"] in TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178:
        return FROZEN_RATIONALE_TYPES_DECREE_1178

    # Default to LAW922
    return FROZEN_RATIONALE_TYPES_LAW_922


def get_change_rationale_types(tender):
    # New causeDetails.scheme logic
    cause_details = tender.get("causeDetails", {})
    cause_scheme = cause_details.get("scheme")
    if cause_scheme == "DECREE1178":
        return RATIONALE_TYPES_DECREE_1178
    if cause_scheme == "LAW922":
        return RATIONALE_TYPES_LAW_922

    # Some procurementMethodType use DECREE1178
    if tender["procurementMethodType"] in TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178:
        return RATIONALE_TYPES_DECREE_1178

    # Default to LAW922
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
            data["contractChangeRationaleTypes"] = get_change_rationale_types_frozen(tender)
