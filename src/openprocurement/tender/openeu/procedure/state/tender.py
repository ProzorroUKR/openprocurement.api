from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_now, get_request
from openprocurement.tender.core.procedure.awarding import add_next_award
from openprocurement.tender.openeu.procedure.models.award import Award
from openprocurement.tender.core.procedure.models.qualification import Qualification


class OpenEUTenderState(TenderState):
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    @staticmethod
    def add_next_award(request):
        add_next_award(request, award_class=Award)

    def tendering_end_handler(self, tender):
        for complaint in tender.get("complaints", ""):
            if complaint.get("status") == "answered" and complaint.get("resolutionType"):
                complaint["status"] = complaint["resolutionType"]

        handler = self.get_change_tender_status_handler("active.pre-qualification")
        handler(tender)
        tender["qualificationPeriod"] = {"startDate": get_now().isoformat()}

        self.remove_draft_bids(tender)
        self.check_bids_number(tender)
        self.prepare_qualifications(tender)

    def prepare_qualifications(self, tender):
        if "qualifications" not in tender:
            tender["qualifications"] = []
        bids = tender.get("bids", "")
        lots = tender.get("lots")
        if lots:
            active_lots = tuple(lot["id"] for lot in lots if lot["status"] == "active")
            for bid in bids:
                if bid["status"] not in ("invalid", "deleted"):
                    for lotValue in bid.get("lotValues", ""):
                        if lotValue["status"] == "pending" and lotValue["relatedLot"] in active_lots:
                            qualification = Qualification({
                                "bidID": bid["id"],
                                "status": "pending",
                                "lotID": lotValue["relatedLot"],
                                "date": get_now().isoformat()
                            }).serialize()
                            tender["qualifications"].append(qualification)
        else:
            for bid in bids:
                if bid["status"] == "pending":
                    qualification = Qualification({
                        "bidID": bid["id"],
                        "status": "pending",
                        "date": get_now().isoformat()
                    }).serialize()
                    tender["qualifications"].append(qualification)

    def cancellation_compl_period_end_handler(self, cancellation):
        def handler(tender):
            complaint_statuses = ("invalid", "declined", "stopped", "mistaken", "draft")
            if all(i["status"] in complaint_statuses for i in cancellation.get("complaints", "")):
                cancellation["status"] = "active"

                from openprocurement.tender.core.validation import (
                    validate_absence_of_pending_accepted_satisfied_complaints,
                )
                # TODO: chronograph expects 422 errors ?
                validate_absence_of_pending_accepted_satisfied_complaints(get_request(), cancellation)
                if cancellation.get("relatedLot"):
                    # 1
                    related_lot = cancellation["relatedLot"]
                    for lot in tender["lots"]:
                        if lot["id"] == related_lot:
                            lot["status"] = "cancelled"

                    # 2
                    cancelled_lots = {i["id"] for i in tender.get("lots") if i["status"] == "cancelled"}
                    cancelled_items = {i["id"] for i in tender.get("items", "")
                                       if i.get("relatedLot") in cancelled_lots}
                    cancelled_features = {
                        i["code"]
                        for i in tender.get("features", "")
                        if i["featureOf"] == "lot" and i["relatedItem"] in cancelled_lots
                        or i["featureOf"] == "item" and i["relatedItem"] in cancelled_items
                    }

                    # 3
                    if tender["status"] in (
                        "active.tendering",
                        "active.pre-qualification",
                        "active.pre-qualification.stand-still",
                        "active.auction",
                    ):
                        def filter_docs(b, key):
                            if b.get(key):
                                b[key] = [i for i in b[key]
                                          if i.get("documentOf") != "lot"
                                          or i["relatedItem"] not in cancelled_lots]

                        for bid in tender.get("bids", ""):
                            if tender["status"] == "active.tendering":
                                filter_docs(bid, "documents")
                            filter_docs(bid, "financialDocuments")
                            filter_docs(bid, "eligibilityDocuments")
                            filter_docs(bid, "qualificationDocuments")
                            bid["parameters"] = [i for i in bid.get("parameters", "")
                                                 if i["code"] not in cancelled_features]
                            bid["lotValues"] = [i for i in bid.get("lotValues", "")
                                                if i["relatedLot"] not in cancelled_lots]
                            if not bid["lotValues"] and bid["status"] in ["pending", "active"]:
                                if tender["status"] == "active.tendering":
                                    bid["status"] = "invalid"
                                else:
                                    bid["status"] = "invalid.pre-qualification"

                    # 4
                    lot_statuses = {lot["status"] for lot in tender["lots"]}
                    if lot_statuses == {"cancelled"}:
                        tender["status"] = "cancelled"
                    elif not lot_statuses.difference({"unsuccessful", "cancelled"}):
                        tender["status"] = "unsuccessful"
                    elif not lot_statuses.difference({"complete", "unsuccessful", "cancelled"}):
                        tender["status"] = "complete"

                    # 5
                    if tender["status"] == "active.auction" and all(
                            i.get("auctionPeriod", {}).get("endDate")
                            for i in tender["lots"]
                            if i["status"] == "active"   # TODO: no checks for bids count (like in core method)
                    ):
                        self.add_next_award(get_request())
                else:
                    if tender["status"] == "active.tendering":
                        tender["bids"] = []
                    elif tender["status"] in (
                        "active.pre-qualification",
                        "active.pre-qualification.stand-still",
                        "active.auction",
                    ):
                        for bid in tender.get("bids", ""):
                            if bid["status"] in ("pending", "active"):
                                bid["status"] = "invalid.pre-qualification"
                                # which doesn't delete data, but they are hidden by serialization functionality
                    tender["status"] = "cancelled"
        return handler
