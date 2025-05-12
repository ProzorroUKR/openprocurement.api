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
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.utils import calculate_date, context_unpack
from openprocurement.tender.core.procedure.utils import (
    calc_auction_replan_time,
    dt_from_iso,
    normalize_should_start_after,
)
from openprocurement.tender.core.utils import QUICK

LOGGER = getLogger(__name__)


class ShouldStartAfterMixing:
    def calc_auction_periods(self, tender):
        if tender["config"]["hasAuction"] is False:
            return

        for complaint in tender.get("complaints", ""):
            if complaint.get("status") in self.block_complaint_status:
                return

        quick = SANDBOX_MODE and QUICK in tender.get("submissionMethodDetails", "")
        lots = tender.get("lots")
        if lots:
            for lot_num, lot in enumerate(lots):
                period = lot.get("auctionPeriod", {})
                start_after = self.get_lot_auction_should_start_after(tender, lot)
                if start_after:
                    number_of_bids = self.count_lot_bids_number(tender, lot["id"])
                    self.update_auction_period_start_dates(
                        period=period,
                        should_start_after=start_after,
                        number_of_bids=number_of_bids,
                        quick=quick,
                        lot_id=lot["id"],
                    )
                    lot["auctionPeriod"] = period

                elif "shouldStartAfter" in period:
                    del period["shouldStartAfter"]
                    if not period:
                        del lot["auctionPeriod"]

        else:
            period = tender.get("auctionPeriod", {})
            start_after = self.get_auction_should_start_after(tender)
            if start_after:
                number_of_bids = self.count_bids_number(tender)
                self.update_auction_period_start_dates(
                    period=period,
                    should_start_after=start_after,
                    number_of_bids=number_of_bids,
                    quick=quick,
                )
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

        return self.get_should_start_after(tender)

    def get_should_start_after(self, tender):
        if tender["config"]["hasPrequalification"]:
            qualification_period = tender.get("qualificationPeriod")
            if qualification_period and qualification_period.get("endDate"):
                complaints_unblock_dates = self.get_tender_qualification_complaints_unblock_dates(tender)
                complaints_unblock_dates.append(dt_from_iso(qualification_period["endDate"]))
                start_after = max(complaints_unblock_dates)
                return normalize_should_start_after(start_after, tender).isoformat()
        else:
            complaints_unblock_dates = self.get_tender_complaints_unblock_dates(tender)
            complaints_unblock_dates.append(dt_from_iso(tender["tenderPeriod"]["endDate"]))
            start_after = max(complaints_unblock_dates)
            return normalize_should_start_after(start_after, tender).isoformat()

    @staticmethod
    def get_auction_should_start_after_allowed_statuses(tender):
        if tender["config"]["hasPrequalification"]:
            return ("active.pre-qualification.stand-still", "active.auction")
        else:
            return ("active.tendering", "active.auction")

    @classmethod
    def get_tender_complaints_unblock_dates(cls, tender):
        complaints = tender.get("complaints", "")
        return cls.get_complaints_unblock_dates(complaints)

    @classmethod
    def get_tender_qualification_complaints_unblock_dates(cls, tender):
        unblock_dates = []
        for qualification in tender.get("qualifications", ""):
            complaints = qualification.get("complaints", "")
            unblock_dates.extend(cls.get_complaints_unblock_dates(complaints))
        return unblock_dates

    @classmethod
    def get_complaints_unblock_dates(cls, complaints):
        unblock_dates = []
        for complaint in complaints:
            if complaint.get("status") in cls.block_complaint_status:
                # if there is any blocking complaint, auction should not be replanned yet
                return []
            if complaint.get("tendererActionDate"):
                # satisfied complaints unblock on tendererActionDate
                date = dt_from_iso(complaint["tendererActionDate"])
                unblock_dates.append(date)
            elif complaint.get("dateDecision"):
                # other blocking complaints unblock on dateDecision
                date = dt_from_iso(complaint["dateDecision"])
                unblock_dates.append(date)
        return unblock_dates

    def update_auction_period_start_dates(
        self, *, period: dict[str, str], should_start_after: str, number_of_bids: int, quick: bool, lot_id: str = None
    ) -> None:
        should_start_after_before = period.get("shouldStartAfter")
        period["shouldStartAfter"] = should_start_after

        start_date = period.get("startDate")
        end_date = period.get("endDate")

        # Not planned yet
        if start_date is None:
            period["startDate"] = self.get_auction_start_date(should_start_after, quick)
            LOGGER.info(
                "Planned auction at %s",
                period["startDate"],
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "auction_planned"},
                    {"LOT_ID": lot_id},
                ),
            )
            return

        # ShouldStartAfter was moved forward when tenderPeriod was extended
        if start_date < should_start_after:
            period["startDate"] = self.get_auction_start_date(should_start_after, quick)
            LOGGER.info(
                "Replanned auction at %s because shouldStartAfter was moved forward",
                period["startDate"],
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "auction_replanned"},
                    {"LOT_ID": lot_id},
                ),
            )
            return

        # shouldStartAfter was moved earlier when tenderPeriod was shortened
        # do not replan if delta is small
        if should_start_after_before is not None:
            date_before = datetime.fromisoformat(should_start_after_before)
            date_after = datetime.fromisoformat(should_start_after)
            should_start_days_delta = (date_before - date_after).days
            if should_start_days_delta > AUCTION_PERIOD_SHOULD_START_EARLIER_UPDATE_DAYS:
                period["startDate"] = self.get_auction_start_date(should_start_after, quick)
                LOGGER.info(
                    "Replanned auction at %s because shouldStartAfter was moved earlier",
                    period["startDate"],
                    extra=context_unpack(
                        get_request(),
                        {"MESSAGE_ID": "auction_replanned"},
                        {"LOT_ID": lot_id},
                    ),
                )
                return

        # auction is not finished in time
        # endDate is not set when it is seems it should be (+ buffer time)
        # chronograph will be scheduled at this time
        replan_time = calc_auction_replan_time(number_of_bids, dt_from_iso(start_date))
        if end_date is None and replan_time < get_request_now():
            period["startDate"] = self.get_auction_start_date(should_start_after, quick)
            LOGGER.warning(
                "Replanned auction at %s because it was not finished in time",
                period["startDate"],
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "auction_replanned"},
                    {"LOT_ID": lot_id},
                ),
            )
            return

    @staticmethod
    def get_auction_start_date(should_start_after: str, quick: bool) -> str:
        # get auction start DATE
        start_dt = max(
            dt_from_iso(should_start_after),
            get_request_now(),
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
