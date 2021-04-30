from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.utils import is_item_owner
from openprocurement.tender.openua.procedure.serializers import BidSerializer as BaseBidSerializer


class BidSerializer(BaseBidSerializer):
    whitelist = None

    def __init__(self, data: dict):
        super().__init__(data)
        tender_status = get_tender()["status"]
        if data["status"] in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}
        elif tender_status in ("active.pre-qualification", "active.pre-qualification.stand-still"):
            self.whitelist = {"id", "status", "documents", "tenderers", "requirementResponses"}

        elif tender_status == "active.auction":
            self.whitelist = {"id", "status", "documents", "tenderers"}
        elif tender_status in ("active.stage2.pending", "active.stage2.waiting"):
            self.whitelist = {"id", "status", "documents", "tenderers"}
        elif tender_status == "unsuccessful":
            self.whitelist = {
                "id", "status", "tenderers", "documents", "selfQualified", "selfEligible",
                "subcontractingDetails", "requirementResponses",
            }
        # elif is_item_owner(get_request(), data):
        #     pass  # bid_role = "view"

    @property
    def data(self) -> dict:
        if self.whitelist:
            data = {
                k: self.serialize_value(k, v)
                for k, v in self._data.items()
                if k in self.whitelist
            }
            return data
        return super().data
