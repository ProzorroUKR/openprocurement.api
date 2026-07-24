from openprocurement.api.deprecated.rationale_types import CAUSE_TO_FROZEN_RATIONALE_TYPES_MAPPING
from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)
from openprocurement.contracting.core.procedure.serializers.rationale_types import (
    ContractChangeRationaleTypesSerializer,
    get_change_rationale_types_reference,
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
        "contractChangeRationaleTypes": ContractChangeRationaleTypesSerializer,  # TODO: remove after migration
    }

    def __init__(self, data: dict, tender=None, **kwargs):
        super().__init__(data, tender=tender, **kwargs)

        if tender and not data.get("contractChangeRationaleTypes"):
            # Now tenders use lists from standards library to populate rationale types on tender creation time
            # Old tenders use frozen lists of rationale types, and here we populate the field with the frozen list
            mapping = CAUSE_TO_FROZEN_RATIONALE_TYPES_MAPPING
            data["contractChangeRationaleTypes"] = get_change_rationale_types_reference(tender, mapping)
