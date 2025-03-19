import random
from datetime import datetime, timedelta
from logging import getLogger

from dateorro import calc_nearest_working_datetime

from openprocurement.api.constants import (
    AUCTION_DAY_START,
    AUCTION_PERIOD_SHOULD_START_EARLIER_UPDATE_DAYS,
    AUCTION_TIME_SLOTS_NUMBER,
    HALF_HOUR_SECONDS,
    SANDBOX_MODE,
    TZ,
    WORKING_DAYS,
)
from openprocurement.api.context import get_now
from openprocurement.api.utils import calculate_date
from openprocurement.tender.core.procedure.utils import (
    calc_auction_end_time,
    dt_from_iso,
    normalize_should_start_after,
)
from openprocurement.tender.core.utils import QUICK

LOGGER = getLogger(__name__)


class ShouldStartAfterMixing:
    def calc_auction_periods(self, tender):
        if tender["config"]["hasAuction"] is False:
            return

        quick = SANDBOX_MODE and QUICK in tender.get("submissionMethodDetails", "")
        lots = tender.get("lots")
        if lots:
            for lot_num, lot in enumerate(lots):
                period = lot.get("auctionPeriod", {})
                start_after = self.get_lot_auction_should_start_after(tender, lot)
                if start_after:
                    self.update_auction_period_start_dates(period=period, should_start_after=start_after, quick=quick)
                    lot["auctionPeriod"] = period

                elif "shouldStartAfter" in period:
                    del period["shouldStartAfter"]
                    if not period:
                        del lot["auctionPeriod"]

        else:
            period = tender.get("auctionPeriod", {})
            start_after = self.get_auction_should_start_after(tender)
            if start_after:
                self.update_auction_period_start_dates(period=period, should_start_after=start_after, quick=quick)
                tender["auctionPeriod"] = period

            elif "shouldStartAfter" in period:
                del period["shouldStartAfter"]
                if not period:
                    del tender["auctionPeriod"]

    def get_lot_auction_should_start_after(self, tender, lot):
        allowed_statuses = self.get_auction_should_start_after_allowed_statuses(tender)
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

        return self.get_should_start_after(tender)

    def get_auction_should_start_after(self, tender):
        allowed_statuses = self.get_auction_should_start_after_allowed_statuses(tender)
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
        if tender["config"]["hasPrequalification"]:
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
    def get_auction_should_start_after_allowed_statuses(tender):
        if tender["config"]["hasPrequalification"]:
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
            complaints = qualification.get("complaints", "")
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

    def update_auction_period_start_dates(
        self, *, period: dict[str, str], should_start_after: str, quick: bool
    ) -> None:
        # update "shouldStartAfter"
        start_after_before = period.get("shouldStartAfter")
        period["shouldStartAfter"] = should_start_after

        # update "startDate"
        should_start_moved_earlier = (
            start_after_before is not None
            and (datetime.fromisoformat(start_after_before) - datetime.fromisoformat(should_start_after)).days
            > AUCTION_PERIOD_SHOULD_START_EARLIER_UPDATE_DAYS
        )
        start_date = period.get("startDate")
        if start_date is None or start_date < should_start_after or should_start_moved_earlier:
            period["startDate"] = self.get_auction_start_date(should_start_after, quick)

    @staticmethod
    def get_auction_start_date(should_start_after: str, quick: bool) -> str:
        # get auction start DATE
        start_dt = max(
            dt_from_iso(should_start_after),
            get_now(),
        )
        if quick:
            return (start_dt + timedelta(seconds=60)).isoformat()

        start_dt += timedelta(hours=1)
        start_dt = calc_nearest_working_datetime(start_dt, calendar=WORKING_DAYS)
        if start_dt.time() >= AUCTION_DAY_START:
            start_dt = calculate_date(start_dt, timedelta(days=1), working_days=True)
        start_date = start_dt.date()

        # get auction start TIME
        time_slot_number = random.randrange(0, AUCTION_TIME_SLOTS_NUMBER)
        auction_start = (
            datetime.combine(start_date, AUCTION_DAY_START)
            + timedelta(seconds=HALF_HOUR_SECONDS * time_slot_number)  # schedule to the timeslot
            + timedelta(  # randomize time within the timeslot
                seconds=random.randrange(0, HALF_HOUR_SECONDS),
                milliseconds=random.randrange(0, 1000),
            )
        )
        return TZ.localize(auction_start).isoformat()
