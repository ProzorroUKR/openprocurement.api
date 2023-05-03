from openprocurement.api.constants import TZ
from openprocurement.tender.core.procedure.context import (
    get_tender_config,
)
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    normalize_should_start_after,
)
from openprocurement.tender.core.utils import calc_auction_end_time
from datetime import timedelta, datetime, time
from logging import getLogger


LOGGER = getLogger(__name__)


class BaseShouldStartAfterMixing:
    count_bids_number: callable
    count_lot_bids_number: callable

    def get_lot_auction_should_start_after(self, tender, lot):
        if tender.get("status") not in ("active.tendering", "active.auction"):
            return
        period = lot.get("auctionPeriod") or {}
        if period.get("endDate") or lot.get("status", "active") != "active":
            return
        number_of_bids = self.count_lot_bids_number(tender, lot["id"])
        if tender["status"] == "active.auction" and number_of_bids < 2:
            return  # there is no sense to run this auction, shouldStartAfter should be deleted

        start_date = period.get("startDate")
        if start_date:
            expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
            if get_now() > expected_value:
                return normalize_should_start_after(expected_value, tender).isoformat()

        decision_dates = [
            dt_from_iso(complaint["dateDecision"]).replace(
                hour=0, minute=0, second=0, microsecond=0,
            ) + timedelta(days=3)
            for complaint in tender.get("complaints", "")
            if complaint.get("dateDecision")
        ]
        decision_dates.append(dt_from_iso(tender["tenderPeriod"]["endDate"]))
        start_after = max(decision_dates)
        return normalize_should_start_after(start_after, tender).isoformat()

    def get_auction_should_start_after(self, tender):
        if tender.get("status") not in ("active.tendering", "active.auction"):
            return
        period = tender.get("auctionPeriod") or {}
        if not period.get("endDate"):
            start_date = period.get("startDate")
            if start_date:
                number_of_bids = self.count_bids_number(tender)
                expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
                if get_now() > expected_value:
                    return normalize_should_start_after(expected_value, tender).isoformat()

            decision_dates = [
                datetime.combine(
                    dt_from_iso(complaint["dateDecision"]) + timedelta(days=3),
                    time(0, tzinfo=TZ)
                )
                for complaint in tender.get("complaints", "")
                if complaint.get("dateDecision")
            ]
            decision_dates.append(dt_from_iso(tender["tenderPeriod"]["endDate"]))
            start_after = max(decision_dates)
            return normalize_should_start_after(start_after, tender).isoformat()

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


class PreQualificationShouldStartAfterMixing(BaseShouldStartAfterMixing):

    @staticmethod
    def _get_decision_dates(tender):
        decision_dates = []
        for qualification in tender.get("qualifications", ""):
            for complaint in qualification.get("complaints", ""):
                if complaint.get("dateDecision"):
                    date = dt_from_iso(complaint["dateDecision"]) + timedelta(days=3)
                    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                    decision_dates.append(date)
        return decision_dates

    def get_lot_auction_should_start_after(self, tender, lot):
        tender_status = tender.get("status")
        if tender_status in ("active.pre-qualification.stand-still", "active.auction"):
            period = lot.get("auctionPeriod") or {}
            if not period.get("endDate") and lot.get("status", "active") == "active":
                number_of_bids = self.count_lot_bids_number(tender, lot["id"])
                if tender["status"] == "active.auction" and number_of_bids < 2:
                    return  # there is no sense to run this auction, shouldStartAfter should be deleted

                start_date = period.get("startDate")
                if start_date:
                    expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
                    if get_now() > expected_value:
                        return normalize_should_start_after(expected_value, tender).isoformat()

                qualification_period = tender.get("qualificationPeriod")
                if qualification_period and qualification_period.get("endDate"):
                    decision_dates = self._get_decision_dates(tender)
                    decision_dates.append(dt_from_iso(qualification_period["endDate"]))
                    start_after = max(decision_dates)
                    return normalize_should_start_after(start_after, tender).isoformat()

    def get_auction_should_start_after(self, tender):
        tender_status = tender.get("status")
        if tender_status in ("active.pre-qualification.stand-still", "active.auction"):
            period = tender.get("auctionPeriod") or {}
            if not period.get("endDate"):
                start_date = period.get("startDate")
                if start_date:
                    number_of_bids = self.count_bids_number(tender)
                    expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
                    if get_now() > expected_value:
                        return normalize_should_start_after(expected_value, tender).isoformat()

                qualification_period = tender.get("qualificationPeriod")
                if qualification_period and qualification_period.get("endDate"):
                    decision_dates = self._get_decision_dates(tender)
                    decision_dates.append(dt_from_iso(qualification_period["endDate"]))
                    start_after = max(decision_dates)
                    return normalize_should_start_after(start_after, tender).isoformat()
