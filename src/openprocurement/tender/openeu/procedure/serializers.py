from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer as BaseBidSerializer


def serialize_role(bid):
    # TODO get rid of this function
    if bid["status"] not in ("draft", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"):
        tender = get_tender()
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


class BidSerializer(BaseBidSerializer):

    def __init__(self, data: dict):
        super().__init__(data)
        bid_role = serialize_role(data)
        if bid_role in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}
        elif bid_role == "invalid.pre-qualification":
            self.whitelist = {"id", "status", "documents", "eligibilityDocuments",
                              "tenderers", "requirementResponses"}
        elif bid_role == "unsuccessful":
            self.whitelist = {
                "id", "status", "tenderers", "documents", "eligibilityDocuments", "parameters",
                "selfQualified", "selfEligible", "subcontractingDetails", "requirementResponses",
            }
        elif is_item_owner(get_request(), data):
            pass  # bid_role = "view"
        else:  # based on tender status
            tender = get_tender()  # bid_role = tender["status"]
            if tender["status"].startswith("active.pre-qualification"):
                self.whitelist = {"id", "status", "documents", "eligibilityDocuments",
                                  "tenderers", "requirementResponses"}
            elif tender["status"] == "active.auction":
                self.whitelist = {"id", "status", "documents", "eligibilityDocuments", "tenderers"}
