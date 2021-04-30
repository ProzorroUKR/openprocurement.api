from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.utils import is_item_owner
from openprocurement.tender.openua.procedure.serializers import (
    BidSerializer as BaseBidSerializer,
)


class BidSerializer(BaseBidSerializer):
    whitelist = None

    def __init__(self, data: dict):
        super().__init__(data)
        tender = get_tender()
        if data["status"] in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}

        elif tender["status"] in ("invalid.pre-qualification", "active.pre-qualification",
                                  "active.pre-qualification.stand-still", "active.auction"):
            self.whitelist = {"id", "status", "tenderers", "documents", "eligibilityDocuments", "requirementResponses"}

        elif data["status"] == "unsuccessful":
            self.whitelist = {
                "id", "status", "tenderers", "documents", "eligibilityDocuments", "requirementResponses",
                "selfEligible", "selfQualified", "parameters", "subcontractingDetails",
            }
        elif is_item_owner(get_request(), data):
            pass  # bid_role = "view"
            self.whitelist = {
                "id", "date", "participationUrl",
                "selfEligible", "selfQualified",
                "documents", "eligibilityDocuments", "financialDocuments", "qualificationDocuments",
                "value", "lotValues", "parameters", "subcontractingDetails",
                "tenderers", "status", "requirementResponses"
            }
