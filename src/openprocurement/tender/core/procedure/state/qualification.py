from openprocurement.tender.core.procedure.state.tender import TenderState
from logging import getLogger
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.qualification import Qualification


LOGGER = getLogger(__name__)


class QualificationState(TenderState):

    @property
    def tender(self):
        return self.request.validated["tender"]

    @staticmethod
    def prepare_qualifications(tender, bids: list, lot_id: str = None):
        """ creates Qualification for each Bid
        """
        if "qualifications" not in tender:
            tender["qualifications"] = []
        new_qualifications = []
        if not bids:
            bids = tender.get("bids", "")
        lots = tender.get("lots")
        if "lots" in tender:
            active_lots = [lot["id"] for lot in lots if lot.get("status") == "active"]
            for bid in bids:
                if bid.get("status") not in ["invalid", "deleted"]:
                    for lotValue in bid.get("lotValues", ""):
                        if lotValue.get("status", "pending") == "pending" and lotValue["relatedLot"] in active_lots:
                            if lot_id and lotValue["relatedLot"] == lot_id:
                                qualification = Qualification({
                                    "bidID": bid["id"],
                                    "status": "pending",
                                    "lotID": lot_id,
                                    "date": get_now().isoformat()
                                }).serialize()
                                tender["qualifications"].append(qualification)
                                new_qualifications.append(qualification["id"])
        else:
            for bid in bids:
                if bid["status"] == "pending":
                    qualification = Qualification({
                        "bidID": bid["id"],
                        "status": "pending",
                        "date": get_now().isoformat()
                    }).serialize()
                    tender["qualifications"].append(qualification)
                    new_qualifications.append(qualification["id"])
        return new_qualifications

    def set_bid_status(self, bid_id, status, lot_id=None):
        if lot_id:
            for bid in self.tender["bids"]:
                if bid["id"] == bid_id:
                    for lotValue in bid["lotValues"]:
                        if lotValue["relatedLot"] == lot_id:
                            self.set_object_status(lotValue, status)
                            if status in ["active", "pending"]:
                                bid["status"] = status
                            self.pull_up_bid_status(self.tender, bid)
                            return bid
        for bid in self.tender["bids"]:
            if bid["id"] == bid_id:
                bid["status"] = status
                return bid

    @staticmethod
    def pull_up_bid_status(tender, bid):
        lots = tender.get("lots", "")
        if lots:
            lot_values = bid.get("lotValues")
            if not lot_values:
                bid["status"] = "invalid"

            active_lots = {lot["id"] for lot in lots if lot["status"] in ("active", "complete")}
            lot_values_statuses = {lv["status"] for lv in lot_values if lv["relatedLot"] in active_lots}
            if "pending" in lot_values_statuses:
                bid["status"] = "pending"

            elif "active" in lot_values_statuses:
                bid["status"] = "active"
            else:
                bid["status"] = "unsuccessful"

    def qualification_on_patch(self, before, qualification):
        if before["status"] != qualification["status"]:
            self.qualification_status_up(before["status"], qualification["status"], qualification)
        elif before["status"] != "pending":
            raise_operation_error(self.request, "Can't update qualification status")

    def qualification_status_up(self, before, after, qualification):
        qualification["date"] = get_now().isoformat()
        bid_id = qualification["bidID"]
        lot_id = qualification.get("lotID")
        if before != "pending" and after != "cancelled":
            raise_operation_error(self.request, "Can't update qualification status")
        if after == "active":
            # approve related bid
            self.set_bid_status(bid_id, "active", lot_id)
        elif after == "unsuccessful":
            # cancel related bid
            self.set_bid_status(bid_id, "unsuccessful", lot_id)
        elif after == "cancelled":
            # return bid to initial status
            bid = self.set_bid_status(bid_id, "pending", lot_id)
            # generate new qualification for related bid
            ids = self.prepare_qualifications(self.tender, bids=[bid], lot_id=lot_id)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Qualification".format(self.tender["procurementMethodType"]),
                tender_id=self.tender["tenderID"],
                qualification_id=ids[0],
            )
