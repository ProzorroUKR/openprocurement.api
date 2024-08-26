from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.serializers.bid import (
    BidSerializer as BaseBidSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


def value_amount_to_float(_, value):
    if isinstance(value, dict) and "amount" in value:
        value["amount"] = float(value["amount"])
    return value


def lot_value_serializer(s, values):
    for item in values:
        if "value" in item:
            item["value"] = value_amount_to_float(s, item["value"])
    return values


class BidSerializer(BaseBidSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "eligibilityDocuments": ListSerializer(DocumentSerializer),
        "qualificationDocuments": ListSerializer(DocumentSerializer),
        "financialDocuments": ListSerializer(DocumentSerializer),
        "value": value_amount_to_float,
        "lotValues": lot_value_serializer,
    }

    whitelist = None

    def __init__(self, data: dict):
        super().__init__(data)
        tender = get_tender()
        if is_item_owner(get_request(), data):
            self.whitelist = None
        elif data["status"] in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}
        elif data["status"] == "unsuccessful":
            self.whitelist = {
                "id",
                "status",
                "tenderers",
                "documents",
                "eligibilityDocuments",
                "requirementResponses",
                "selfEligible",
                "selfQualified",
                "parameters",
                "subcontractingDetails",
            }
        elif tender["status"] in (
            "invalid.pre-qualification",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
        ):
            self.whitelist = {"id", "status", "tenderers", "documents", "eligibilityDocuments", "requirementResponses"}
