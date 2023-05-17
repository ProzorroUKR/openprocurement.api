from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.context import get_tender, get_tender_config
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.utils import is_item_owner


class BidSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }

    def __init__(self, data: dict):
        super().__init__(data)
        config = get_tender_config()

        if config.get("hasPrequalification"):
            # pre-qualification rules
            self.set_tender_with_pre_qualification_whitelist(data)
        else:
            # no pre-qualification rules
            if data.get("status") in ("invalid", "deleted"):
                self.whitelist = {"id", "status"}


    def set_tender_with_pre_qualification_whitelist(self, data):
        tender = get_tender()
        bid_role = self.serialize_role(tender, data)
        if bid_role in ("invalid", "deleted"):
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
        elif is_item_owner(get_request(), data):
            pass  # bid_role = "view"
        else:  # based on tender status
            if tender["status"].startswith("active.pre-qualification"):
                self.whitelist = {
                    "id",
                    "status",
                    "documents",
                    "eligibilityDocuments",
                    "tenderers",
                    "requirementResponses",
                }
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
