from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.utils import calculate_tender_date
from datetime import datetime


class BelowThresholdTenderState(TenderState):
    block_complaint_status = ("answered", "pending")

    # CHILD ITEMS EVENTS --
    def complaint_events(self, tender):
        tender_status = tender.get("status")
        if tender_status.startswith("active"):
            for complaint in tender.get("complaints", ""):
                if complaint["status"] == "answered" and complaint.get("dateAnswered"):
                    check = calculate_tender_date(
                        datetime.fromisoformat(complaint["dateAnswered"]),
                        COMPLAINT_STAND_STILL_TIME,
                        tender
                    )
                    yield check.isoformat(), self.handle_answered_complaint(complaint)

                elif complaint["status"] == "pending":
                    yield tender["dateModified"], self.handle_pending_complaint(complaint)

            for award in tender.get("awards", ""):
                for complaint in award.get("complaints", ""):
                    if complaint["status"] == "answered" and complaint.get("dateAnswered"):
                        check = calculate_tender_date(
                            datetime.fromisoformat(complaint["dateAnswered"]), COMPLAINT_STAND_STILL_TIME, tender)
                        yield check.isoformat(), self.handle_answered_complaint(complaint)
                    elif complaint["status"] == "pending":
                        yield tender["dateModified"], self.handle_pending_complaint(complaint)
    #  -- CHILD ITEMS EVENTS

    # handlers
    @staticmethod
    def handle_answered_complaint(complaint):
        def handler(*_):
            complaint["status"] = complaint["resolutionType"]
        return handler

    @staticmethod
    def handle_pending_complaint(complaint):
        def handler(*_):
            if complaint.get("resolutionType") and complaint.get("dateEscalated"):
                complaint["status"] = complaint["resolutionType"]
            else:
                complaint["status"] = "ignored"
        return handler

    def awarded_complaint_handler(self, tender):
        super().awarded_complaint_handler(tender)
        self.check_ignored_claim(tender)

    # utils
    def check_bids_number(self, tender):
        if tender.get("lots"):
            for lot in tender["lots"]:
                bid_number = self.count_lot_bids_number(tender, lot["id"])
                if bid_number < 2:
                    if lot.get("auctionPeriod", {}).get("startDate"):
                        del lot["auctionPeriod"]["startDate"]
                        if not lot["auctionPeriod"]:
                            del lot["auctionPeriod"]

                    if bid_number == 0 and lot["status"] == "active":
                        lot["status"] = "unsuccessful"

            self.cleanup_bids_for_cancelled_lots(tender)
            if not set(i["status"] for i in tender["lots"]).difference({"unsuccessful", "cancelled"}):
                self.get_change_tender_status_handler("unsuccessful")(tender)

            elif max(self.count_lot_bids_number(tender, i["id"])
                     for i in tender["lots"] if i["status"] == "active") == 1:
                self.add_next_award()
        else:
            bid_number = self.count_bids_number(tender)
            if bid_number < 2 and tender.get("auctionPeriod", {}).get("startDate"):
                del tender["auctionPeriod"]["startDate"]
                if not tender["auctionPeriod"]:
                    del tender["auctionPeriod"]
            if bid_number == 0:
                self.get_change_tender_status_handler("unsuccessful")(tender)
            if bid_number == 1:
                self.add_next_award()
        self.check_ignored_claim(tender)

    @staticmethod
    def cleanup_bids_for_cancelled_lots(tender):
        cancelled_lots = [i["id"] for i in tender["lots"] if i["status"] == "cancelled"]
        if cancelled_lots:
            return
        cancelled_items = [i["id"] for i in tender.get("items", "") if i.get("relatedLot") in cancelled_lots]
        cancelled_features = [
            i["code"]
            for i in tender.get("features", "")
            if i["featureOf"] == "lot" and i["relatedItem"] in cancelled_lots
               or i["featureOf"] == "item" and i["relatedItem"] in cancelled_items
        ]
        for bid in tender.get("bids", ""):
            bid["documents"] = [i for i in bid.get("documents", "")
                                if i.get("documentOf") != "lot" or i.get("relatedItem") not in cancelled_lots]
            bid["parameters"] = [i for i in bid.get("parameters", "")
                                 if i["code"] not in cancelled_features]
            bid["lotValues"] = [i for i in bid.get("lotValues", "")
                                if i["relatedLot"] not in cancelled_lots]
            if not bid["lotValues"]:
                tender["bids"].remove(bid)

    @staticmethod
    def check_ignored_claim(tender):
        statuses = ("complete", "cancelled", "unsuccessful")
        complete_lot_ids = [None] if tender["status"] in statuses else []
        complete_lot_ids.extend([i["id"] for i in tender.get("lots", "")
                                 if i["status"] in statuses])
        for complaint in tender.get("complaints", ""):
            if complaint["status"] == "claim" and complaint.get("relatedLot") in complete_lot_ids:
                complaint["status"] = "ignored"
        for award in tender.get("awards", ""):
            for complaint in award.get("complaints", ""):
                if complaint["status"] == "claim" and complaint.get("relatedLot") in complete_lot_ids:
                    complaint["status"] = "ignored"

    def has_unanswered_tender_complaints(self, tender):
        return False

    def has_unanswered_tender_questions(self, tender):
        return False
