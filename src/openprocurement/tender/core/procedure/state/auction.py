from datetime import timedelta
from logging import getLogger
from typing import TYPE_CHECKING

from openprocurement.tender.core.procedure.context import get_tender_config
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    normalize_should_start_after,
)
from openprocurement.tender.core.utils import calc_auction_end_time

LOGGER = getLogger(__name__)

if TYPE_CHECKING:
    from openprocurement.tender.core.procedure.state.tender import (
        TenderStateAwardingMixing,
        ChronographEventsMixing,
        BaseState,
    )
    class baseclass(TenderStateAwardingMixing, ChronographEventsMixing, BaseState):
        pass
else:
    baseclass = object


class ShouldStartAfterMixing(baseclass):

    def calc_auction_periods(self, tender):
        config = get_tender_config()
        if config.get("hasAuction") is False:
            return

        lots = tender.get("lots")
        if lots:
            for lot in lots:
                period = lot.get("auctionPeriod", {})
                start_after = self.get_lot_auction_should_start_after(tender, lot)
                if start_after:
                    period["shouldStartAfter"] = start_after
                    lot["auctionPeriod"] = period

                elif "shouldStartAfter" in period:
                    del period["shouldStartAfter"]
                    if not period:
                        del lot["auctionPeriod"]

        else:
            period = tender.get("auctionPeriod", {})
            start_after = self.get_auction_should_start_after(tender)
            if start_after:
                period["shouldStartAfter"] = start_after
                tender["auctionPeriod"] = period

            elif "shouldStartAfter" in period:
                del period["shouldStartAfter"]
                if not period:
                    del tender["auctionPeriod"]

    def get_lot_auction_should_start_after(self, tender, lot):
        allowed_statuses = self.get_auction_should_start_after_allowed_statuses()
        if tender.get("status") not in allowed_statuses:
            return

        period = lot.get("auctionPeriod") or {}
        if period.get("endDate"):
            return

        if lot.get("status", "active") != "active":
            return

        number_of_bids = self.count_lot_bids_number(tender, lot["id"])
        if tender["status"] == "active.auction" and number_of_bids < 2:
            return  # there is no sense to run this auction, shouldStartAfter should be deleted

        start_date = period.get("startDate")
        if start_date:
            expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
            if get_now() > expected_value:
                return normalize_should_start_after(expected_value, tender).isoformat()

        return self.get_should_start_after(tender)

    def get_auction_should_start_after(self, tender):
        allowed_statuses = self.get_auction_should_start_after_allowed_statuses()
        if tender.get("status") not in allowed_statuses:
            return

        period = tender.get("auctionPeriod") or {}
        if period.get("endDate"):
            return

        start_date = period.get("startDate")
        if start_date:
            number_of_bids = self.count_bids_number(tender)
            expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
            if get_now() > expected_value:
                return normalize_should_start_after(expected_value, tender).isoformat()

        return self.get_should_start_after(tender)

    def get_should_start_after(self, tender):
        config = get_tender_config()
        if config.get("hasPrequalification"):
            qualification_period = tender.get("qualificationPeriod")
            if qualification_period and qualification_period.get("endDate"):
                decision_dates = self.get_tender_qualification_complaints_decision_dates(tender)
                decision_dates.append(dt_from_iso(qualification_period["endDate"]))
                start_after = max(decision_dates)
                return normalize_should_start_after(start_after, tender).isoformat()
        else:
            decision_dates = self.get_tender_complaints_decision_dates(tender)
            decision_dates.append(dt_from_iso(tender["tenderPeriod"]["endDate"]))
            start_after = max(decision_dates)
            return normalize_should_start_after(start_after, tender).isoformat()

    @staticmethod
    def get_auction_should_start_after_allowed_statuses():
        if get_tender_config().get("hasPrequalification"):
            return ("active.pre-qualification.stand-still", "active.auction")
        else:
            return ("active.tendering", "active.auction")

    @classmethod
    def get_tender_complaints_decision_dates(cls, tender):
        complaints = tender.get("complaints", "")
        return cls.get_complaints_decision_dates(complaints)

    @classmethod
    def get_tender_qualification_complaints_decision_dates(cls, tender):
        decision_dates = []
        for qualification in tender.get("qualifications", ""):
            complaints = tender.get("complaints", "")
            decision_dates.extend(cls.get_complaints_decision_dates(complaints))
        return decision_dates

    @staticmethod
    def get_complaints_decision_dates(complaints):
        decision_dates = []
        for complaint in complaints:
            if complaint.get("dateDecision"):
                date = dt_from_iso(complaint["dateDecision"]) + timedelta(days=3)
                date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                decision_dates.append(date)
        return decision_dates
