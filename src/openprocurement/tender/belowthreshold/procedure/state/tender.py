from openprocurement.tender.belowthreshold.procedure.models.award import Award
from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.utils import calculate_tender_date
from datetime import datetime


class BelowThresholdTenderState(TenderState):
    min_bids_number = 1
    block_complaint_status = ()
    award_class = Award

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
    def handle_answered_complaint(self, complaint):
        def handler(*_):
            self.set_object_status(complaint, complaint["resolutionType"])
        return handler

    def handle_pending_complaint(self, complaint):
        def handler(*_):
            if complaint.get("resolutionType") and complaint.get("dateEscalated"):
                self.set_object_status(complaint, complaint["resolutionType"])
            else:
                self.set_object_status(complaint, "ignored")
        return handler

    def awarded_complaint_handler(self, tender):
        super().awarded_complaint_handler(tender)
        self.check_ignored_claim(tender)

    # utils
    def check_bids_number(self, tender):
        super().check_bids_number(tender)
        self.check_ignored_claim(tender)


    def check_ignored_claim(self, tender):
        statuses = ("complete", "cancelled", "unsuccessful")
        complete_lot_ids = [None] if tender["status"] in statuses else []
        complete_lot_ids.extend([i["id"] for i in tender.get("lots", "")
                                 if i["status"] in statuses])
        for complaint in tender.get("complaints", ""):
            if complaint["status"] == "claim" and complaint.get("relatedLot") in complete_lot_ids:
                self.set_object_status(complaint, "ignored")
        for award in tender.get("awards", ""):
            for complaint in award.get("complaints", ""):
                if complaint["status"] == "claim" and complaint.get("relatedLot") in complete_lot_ids:
                    self.set_object_status(complaint, "ignored")

    def has_unanswered_tender_complaints(self, tender):
        return False

    def has_unanswered_tender_questions(self, tender):
        return False

    @staticmethod
    def check_skip_award_complaint_period():
        return True
