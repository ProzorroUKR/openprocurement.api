from copy import deepcopy

from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.serializers.item import (
    ItemPreQualificationSerializer,
)


class BidSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "eligibilityDocuments": ListSerializer(DocumentSerializer),
        "financialDocuments": ListSerializer(DocumentSerializer),
        "qualificationDocuments": ListSerializer(DocumentSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.serializers = deepcopy(self.serializers)

        tender = get_tender()

        # bid owner should see all fields
        if is_item_owner(get_request(), data):
            return
        elif tender["config"]["hasPrequalification"]:
            # pre-qualification rules
            self.set_tender_with_pre_qualification_whitelist(data)
        else:
            # no pre-qualification rules
            if data.get("status") in ("invalid", "deleted"):
                self.whitelist = {"id", "status"}

    def set_tender_with_pre_qualification_whitelist(self, data):
        tender = get_tender()
        bid_role = self.serialize_role(tender, data)
        if is_item_owner(get_request(), data):
            return  # bid_role = "view"
        elif bid_role in ("invalid", "deleted"):
            self.whitelist = {
                "id",
                "status",
            }
        elif bid_role == "invalid.pre-qualification":
            self.whitelist = {
                "id",
                "status",
                "documents",
                "eligibilityDocuments",
                "tenderers",
                "requirementResponses",
            }
        elif bid_role == "unsuccessful":
            self.whitelist = {
                "id",
                "status",
                "tenderers",
                "documents",
                "eligibilityDocuments",
                "parameters",
                "selfQualified",
                "selfEligible",
                "subcontractingDetails",
                "requirementResponses",
            }
        else:  # based on tender status
            if tender["status"].startswith("active.pre-qualification"):
                self.whitelist = {
                    "id",
                    "status",
                    "documents",
                    "eligibilityDocuments",
                    "tenderers",
                    "requirementResponses",
                    "items",
                }
                self.serializers["items"] = ListSerializer(ItemPreQualificationSerializer)
            elif tender["status"] == "active.auction":
                self.whitelist = {
                    "id",
                    "status",
                    "documents",
                    "eligibilityDocuments",
                    "tenderers",
                }

    def serialize_role(self, tender, bid):
        # TODO: get rid of this function
        if bid["status"] not in (
            "draft",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ):
            if tender["status"] not in ("active.tendering", "cancelled") and tender.get("lots"):
                active_lots = [lot["id"] for lot in tender["lots"] if lot["status"] in ("active", "complete")]
                if not bid.get("lotValues"):
                    return "invalid"
                elif any(i["status"] == "pending" and i["relatedLot"] in active_lots for i in bid["lotValues"]):
                    return "pending"
                elif any(i["status"] == "active" and i["relatedLot"] in active_lots for i in bid["lotValues"]):
                    return "active"
                else:
                    return "unsuccessful"
        return bid["status"]
