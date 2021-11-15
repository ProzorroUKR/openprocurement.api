from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import context_unpack
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.context import get_now, get_request
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    normalize_should_start_after,
    get_first_revision_date,
)
from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.state.utils import cancellation_blocks_tender
from openprocurement.tender.core.utils import calc_auction_end_time
from datetime import timedelta
from logging import getLogger


LOGGER = getLogger(__name__)


class TenderState(TenderStateAwardingMixing, BaseState):
    min_bids_number = 2
    active_bid_statuses = ("active",)  # are you intrigued ?
    # used by bid counting methods

    block_complaint_status = ("answered", "pending")
    block_tender_complaint_status = ("claim", "pending", "accepted", "satisfied", "stopping")
    # tender can't proceed to "active.auction" until has a tender.complaints in one of statuses above

    contract_model = Contract

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        data["date"] = get_now().isoformat()

    def always(self, data):
        super().always(data)

        # this part's come from serializible fields of schematics tender model
        # since we do not convert to schematics the whole tender on every request
        next_check = self.get_next_check(data)
        if next_check is not None:
            data["next_check"] = next_check
        elif "next_check" in data:
            del data["next_check"]
        self.calc_auction_periods(data)

    # CHRONOGRAPH
    # (only tenders are updated by chronograph at the moment)
    def run_time_events(self, data):
        now = get_now().isoformat()
        for date, handler in self.get_events(data):
            # print([date <= now, date, now, handler])
            if date <= now:
                LOGGER.info(f"Applying tender auction chronograph event: {handler}",
                            extra=context_unpack(
                                get_request(), {"MESSAGE_ID": "auction_chronograph_event_apply"}))
                handler(data)

    def get_next_check(self, data):
        events = list(self.get_events(data))
        if events:
            closes_event_time, _ = min(
                events,
                key=lambda e: e[0],  # compare only time
            )
            return closes_event_time

    def get_events(self, tender):
        yield from self.complaint_events(tender)
        yield from self.cancellation_events(tender)

        if not cancellation_blocks_tender(tender):
            status = tender["status"]
            lots = tender.get("lots")
            if status == "active.enquiries":
                if tender.get("tenderPeriod", {}).get("startDate"):
                    yield tender["tenderPeriod"]["startDate"], self.get_change_tender_status_handler("active.tendering")

                elif tender.get("enquiryPeriod", {}).get("endDate"):
                    yield tender["enquiryPeriod"]["endDate"], self.get_change_tender_status_handler("active.tendering")

            elif status == "active.tendering":
                if (
                    tender.get("tenderPeriod", {}).get("endDate")
                    and not self.has_unanswered_tender_complaints(tender)
                    and not self.has_unanswered_tender_questions(tender)
                ):
                    yield tender["tenderPeriod"]["endDate"], self.tendering_end_handler

            elif status == "active.pre-qualification.stand-still":
                yield from self.pre_qualification_stand_still_events(tender)

            elif status == "active.auction":
                if lots:
                    yield from self.lots_auction_events(tender)
                else:
                    yield from self.auction_events(tender)

            elif status == "active.qualification":
                if lots:
                    yield from self.lots_qualification_events(tender)

            elif tender["status"] == "active.qualification.stand-still":  # cfaua, for ex
                yield from self.qualification_stand_still_events(tender)

            elif status == "active.awarded":
                if lots:
                    yield from self.lots_awarded_events(tender)
                else:
                    yield from self.awarded_events(tender)

            yield from self.contract_events(tender)

    # CHILD ITEMS EVENTS --
    def cancellation_events(self, tender):
        now = get_now().isoformat()
        # only for tenders from RELEASE_2020_04_19
        if get_first_revision_date(tender, default=now) >= RELEASE_2020_04_19:
            # no need to check procedures that don't have cancellation complaints  #
            # if tender["procurementMethodType"] not in ("belowThreshold", "closeFrameworkAgreementSelectionUA"):
            for cancellation in tender.get("cancellations", ""):
                if cancellation["status"] == "pending":
                    complaint_period = cancellation.get("complaintPeriod")
                    if complaint_period and complaint_period.get("endDate"):
                        # this check can switch complaint statuses to mistaken + switch cancellation to active
                        yield complaint_period["endDate"], self.cancellation_compl_period_end_handler(cancellation)

    def complaint_events(self, tender):
        now = get_now().isoformat()
        # only for tenders from RELEASE_2020_04_19
        if get_first_revision_date(tender, default=now) >= RELEASE_2020_04_19:
            # all the checks below only supposed to trigger complaint draft->mistaken switches
            # if any object contains a draft complaint, it's complaint end period is added to the checks
            # periods can be in the past, then the check expected to run once and immediately fix the complaint
            complaint_period = tender.get("complaintPeriod")
            if complaint_period and complaint_period.get("endDate"):
                for complaint in tender.get("complaints", ""):
                    if complaint["status"] == "draft" and complaint.get("type", "complaint") == "complaint":
                        yield complaint_period["endDate"], self.draft_complaint_handler(complaint)

            for cancellation in tender.get("cancellations", ""):
                period_end = cancellation.get("complaintPeriod", {}).get("endDate")
                if period_end:
                    for complaint in cancellation.get("complaints", ""):
                        if complaint["status"] == "draft" and complaint.get("type", "complaint") == "complaint":
                            yield period_end, self.draft_complaint_handler(complaint)

            qualification_period = tender.get("qualificationPeriod")
            if qualification_period and qualification_period.get("endDate"):
                for q in tender.get("qualifications", ""):
                    for complaint in q.get("complaints", ""):
                        if complaint["status"] == "draft" and complaint.get("type", "complaint") == "complaint":
                            yield qualification_period["endDate"], self.draft_complaint_handler(complaint)

            for award in tender.get("awards", ""):
                complaint_period = award.get("complaintPeriod")
                if complaint_period and complaint_period.get("endDate"):
                    for complaint in award.get("complaints", ""):
                        if complaint["status"] == "draft" and complaint.get("type", "complaint") == "complaint":
                            yield complaint_period["endDate"], self.draft_complaint_handler(complaint)

    def contract_events(self, tender):
        tender_status = tender.get("status")
        if tender_status.startswith("active"):
            contract_award_ids = {i["awardID"] for i in tender.get("contracts", "")}
            for award in tender.get("awards", ""):
                if award["status"] == "active" and award["id"] not in contract_award_ids:
                    yield award["date"], self.add_next_contract_handler(award)

    #  -- CHILD ITEMS EVENTS

    # TENDER STATUS EVENTS --
    def pre_qualification_stand_still_events(self, tender):

        qualification_period = tender.get("qualificationPeriod")
        if qualification_period and qualification_period.get("endDate"):
            active_lots = [lot["id"] for lot in tender["lots"] if lot["status"] == "active"] \
                if tender.get("lots") else [None]
            if not any(
                complaint["status"] in self.block_complaint_status
                for q in tender.get("qualifications", "")
                for complaint in q.get("complaints", "")
                if q.get("lotID") in active_lots
            ):
                yield qualification_period["endDate"], self.pre_qualification_stand_still_ends_handler

    def auction_events(self, tender):
        auction_period = tender.get("auctionPeriod")
        if auction_period and auction_period.get("startDate") and not auction_period.get("endDate"):
            start_date = auction_period.get("startDate")
            now = get_now().isoformat()
            if now < start_date:
                yield start_date, self.auction_handler
            else:
                auction_end_time = calc_auction_end_time(
                    len(tender.get("bids", "")),
                    dt_from_iso(start_date)
                ).isoformat()
                if now < auction_end_time:
                    yield auction_end_time, self.auction_handler

    def awarded_events(self, tender):  # TODO: move to complaint events ?
        awards = tender.get("awards", [])
        if (
            awards and awards[-1]["status"] == "unsuccessful"
            and not any(c["status"] in self.block_complaint_status for c in tender.get("complaints", ""))
            and not any([c["status"] in self.block_complaint_status
                         for a in awards
                         for c in a.get("complaints", "")])
        ):
            stand_still_ends = [
                a.get("complaintPeriod").get("endDate")
                for a in awards
                if a.get("complaintPeriod") and a.get("complaintPeriod").get("endDate")
            ]
            if stand_still_ends:
                yield max(stand_still_ends), self.awarded_complaint_handler

    def qualification_stand_still_events(self, tender):
        yield from ()

    # lots
    def lots_auction_events(self, tender):
        lots = tender["lots"]
        now = get_now().isoformat()
        for lot in lots:
            if lot["status"] == "active":
                auction_period = lot.get("auctionPeriod", {})
                if auction_period.get("startDate") and not auction_period.get("endDate"):
                    start_date = auction_period.get("startDate")
                    if now < start_date:
                        yield start_date, self.auction_handler
                    else:
                        auction_end_time = calc_auction_end_time(
                            self.count_lot_bids_number(tender, lot["id"]),
                            dt_from_iso(start_date)
                        ).isoformat()
                        if now < auction_end_time:
                            yield auction_end_time, self.auction_handler

    def lots_qualification_events(self, tender):
        lots = tender.get("lots")
        non_lot_complaints = (i for i in tender.get("complaints", "") if i.get("relatedLot") is None)
        if not any(i["status"] in self.block_complaint_status for i in non_lot_complaints):
            for lot in lots:
                if lot["status"] == "active":
                    lot_awards = [i for i in tender.get("awards", "") if i["lotID"] == lot["id"]]
                    if lot_awards and lot_awards[-1]["status"] == "unsuccessful":
                        pending_complaints = any(
                            i["status"] in self.block_complaint_status
                            for i in tender.get("complaints", "")
                            if i.get("relatedLot") == lot["id"]
                        )
                        pending_award_complaints = any(
                            i["status"] in self.block_complaint_status
                            for a in lot_awards
                            for i in a.get("complaints", "")
                        )
                        if not pending_complaints and not pending_award_complaints:
                            stand_still_ends = [
                                a.get("complaintPeriod").get("endDate")
                                for a in lot_awards
                                if a.get("complaintPeriod", {}).get("endDate")
                            ]
                            if stand_still_ends:
                                yield max(stand_still_ends), self.awarded_complaint_handler

    def lots_awarded_events(self, tender):
        yield from self.lots_qualification_events(tender)

    # -- TENDER STATUS EVENTS

    # HANDLERS
    @staticmethod
    def draft_complaint_handler(complaint):
        def handler(*_):
            complaint["status"] = "mistaken"
            complaint["rejectReason"] = "complaintPeriodEnded"
        return handler

    def add_next_contract_handler(self, award):
        def handler(*_):
            request = get_request()
            add_contracts(request, award, self.contract_model)
            self.add_next_award(request)
        return handler

    def get_change_tender_status_handler(self, status):
        def handler(tender):
            before = tender["status"]
            tender["status"] = status
            self.status_up(before, status, tender)
            LOGGER.info(
                f"Switched tender {tender['_id']} to {status}",
                extra=context_unpack(get_request(), {"MESSAGE_ID": f"switched_tender_{status}"}),
            )

        return handler

    def tendering_end_handler(self, tender):
        for complaint in tender.get("complaints", ""):
            if complaint.get("status") == "answered" and complaint.get("resolutionType"):
                complaint["status"] = complaint["resolutionType"]

        handler = self.get_change_tender_status_handler("active.auction")
        handler(tender)

        self.remove_draft_bids(tender)
        self.check_bids_number(tender)

    def pre_qualification_stand_still_ends_handler(self, tender):
        handler = self.get_change_tender_status_handler("active.auction")
        handler(tender)

        self.check_bids_number(tender)

    def awarded_complaint_handler(self, tender):
        if tender.get("lots"):
            self.check_tender_lot_status(tender)

            statuses = {lot["status"] for lot in tender["lots"]}
            if statuses == {"cancelled"}:
                handler = self.get_change_tender_status_handler("cancelled")
                handler(tender)
            elif not statuses.difference({"unsuccessful", "cancelled"}):
                handler = self.get_change_tender_status_handler("unsuccessful")
                handler(tender)
            elif not statuses.difference({"complete", "unsuccessful", "cancelled"}):
                handler = self.get_change_tender_status_handler("complete")
                handler(tender)
        else:
            now = get_now().isoformat()
            pending_complaints = any(i["status"] in self.block_complaint_status
                                     for i in tender.get("complaints", ""))
            pending_awards_complaints = any(
                i["status"] in self.block_complaint_status
                for a in tender.get("awards", "")
                for i in a.get("complaints", "")
            )
            stand_still_ends = [
                a["complaintPeriod"]["endDate"]
                for a in tender.get("awards", "")
                if a.get("complaintPeriod", {}).get("endDate")
            ]
            stand_still_end = max(stand_still_ends) if stand_still_ends else now
            stand_still_time_expired = stand_still_end < now
            last_award_status = tender["awards"][-1]["status"] if tender.get("awards") else ""
            if (
                    last_award_status == "unsuccessful"
                    and not pending_complaints
                    and not pending_awards_complaints
                    and stand_still_time_expired
            ):
                handler = self.get_change_tender_status_handler("unsuccessful")
                handler(tender)

            contracts = (
                tender["agreements"][-1].get("contracts", [])
                if tender.get("agreements")
                else tender.get("contracts", [])
            )
            if (
                    contracts
                    and any(contract["status"] == "active" for contract in contracts)
                    and not any(contract["status"] == "pending" for contract in contracts)
            ):
                handler = self.get_change_tender_status_handler("complete")
                handler(tender)

    def auction_handler(self, _):
        LOGGER.info("Tender auction chronograph event",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "auction_chronograph_event"}))

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
                    related_lot = cancellation["relatedLot"]
                    for lot in tender["lots"]:
                        if lot["id"] == related_lot:
                            lot["status"] = "cancelled"

                    lot_statuses = {lot["status"] for lot in tender["lots"]}
                    if lot_statuses == {"cancelled"}:
                        if tender["status"] in ("active.tendering", "active.auction"):
                            tender["bids"] = []
                        self.get_change_tender_status_handler("cancelled")(tender)

                    elif not lot_statuses.difference({"unsuccessful", "cancelled"}):
                        self.get_change_tender_status_handler("unsuccessful")(tender)
                    elif not lot_statuses.difference({"complete", "unsuccessful", "cancelled"}):
                        self.get_change_tender_status_handler("complete")(tender)

                    # TODO: seems cancellation can block awarding process, refactoring ?
                    # should awarding be also an event
                    # that can be called 1) by auction 2) by chronograph (this case)
                    # if tender["status"] == "active.auction" and all(
                    #         i.get("auctionPeriod", {}).get("endDate")
                    #         for i in tender["lots"]
                    #         if self.count_lot_bids_number(tender, i["id"]) > 1 and i["status"] == "active"
                    # ):
                    #     self.add_next_award(get_request())
                else:
                    if tender["status"] in ("active.tendering", "active.auction"):
                        tender["bids"] = []
                    self.get_change_tender_status_handler("cancelled")(tender)
        return handler

    # UTILS (move to state ?)
    # belowThreshold
    @staticmethod
    def remove_draft_bids(tender):
        if any(bid.get("status", "active") == "draft" for bid in tender.get("bids", "")):
            LOGGER.info("Remove draft bids", extra=context_unpack(get_request(), {"MESSAGE_ID": "remove_draft_bids"}))
            tender["bids"] = [bid for bid in tender["bids"] if bid.get("status", "active") != "draft"]

    def check_bids_number(self, tender):
        if tender.get("lots"):
            for lot in tender["lots"]:
                bid_number = self.count_lot_bids_number(tender, lot["id"])
                if bid_number < self.min_bids_number:
                    if lot.get("auctionPeriod", {}).get("startDate"):
                        del lot["auctionPeriod"]["startDate"]
                        if not lot["auctionPeriod"]:
                            del lot["auctionPeriod"]

                    if lot.get("status") == "active":  # defense procedures doesn't have lot status, for ex
                        lot["status"] = "unsuccessful"

                        # for procedures where lotValues have "status" field (openeu, competitive_dialogue, cfaua, )
                        for bid in tender.get("bids", ""):
                            lot_value_statuses = set()
                            for lot_value in bid.get("lotValues", ""):
                                if "status" in lot_value:
                                    if lot_value["relatedLot"] == lot["id"]:
                                        lot_value["status"] = "unsuccessful"
                                    lot_value_statuses.add(lot_value["status"])
                            if lot_value_statuses == {"unsuccessful"}:
                                bid["status"] = "unsuccessful"

            # should be moved to tender_status_check ?
            if not set(i["status"] for i in tender["lots"]).difference({"unsuccessful", "cancelled"}):
                self.get_change_tender_status_handler("unsuccessful")(tender)
        else:
            bid_number = self.count_bids_number(tender)
            if bid_number < self.min_bids_number:
                if tender.get("auctionPeriod", {}).get("startDate"):
                    del tender["auctionPeriod"]["startDate"]
                    if not tender["auctionPeriod"]:
                        del tender["auctionPeriod"]
                self.get_change_tender_status_handler("unsuccessful")(tender)

    @classmethod
    def count_bids_number(cls, tender):
        count = 0
        for b in tender.get("bids", ""):
            if b.get("status", "active") in cls.active_bid_statuses:
                count += 1
        return count

    @classmethod
    def count_lot_bids_number(cls, tender, lot_id):
        count = 0
        for bid in tender.get("bids", ""):
            for lot_value in bid.get("lotValues", ""):
                if lot_value.get("status", "active") in cls.active_bid_statuses and lot_value["relatedLot"] == lot_id:
                    count += 1
                    break  # proceed to the next bid check
        return count

    @staticmethod
    def check_skip_award_complaint_period(tender):
        skip = (
            tender.get("procurementMethodType") == "belowThreshold"
            and tender.get("procurementMethodRationale") == "simple"
        )
        return skip

    # awarded
    def check_tender_lot_status(self, tender):
        if any(i["status"] in self.block_complaint_status and i.get("relatedLot") is None
               for i in tender.get("complaints", "")):
            return

        now = get_now().isoformat()
        for lot in tender["lots"]:
            if lot["status"] != "active":
                continue

            lot_awards = [i for i in tender.get("awards", "") if i["lotID"] == lot["id"]]
            if not lot_awards:
                continue

            last_award = lot_awards[-1]
            pending_complaints = any(
                i["status"] in self.block_complaint_status and i["relatedLot"] == lot["id"]
                for i in tender.get("complaints", "")
            )
            pending_awards_complaints = any(
                [i["status"] in self.block_complaint_status
                 for a in lot_awards
                 for i in a.get("complaints", "")]
            )
            stand_still_ends = [
                a["complaintPeriod"]["endDate"]
                for a in lot_awards
                if a.get("complaintPeriod", {}).get("endDate")
            ]
            stand_still_end = max(stand_still_ends) if stand_still_ends else now
            in_stand_still = now < stand_still_end
            skip_award_complaint_period = self.check_skip_award_complaint_period(tender)
            if (
                    pending_complaints
                    or pending_awards_complaints
                    or (in_stand_still and not skip_award_complaint_period)
            ):
                continue

            elif last_award["status"] == "unsuccessful":
                LOGGER.info(
                    f"Switched lot {lot['id']} of tender {tender['_id']} to unsuccessful",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_lot_unsuccessful"},
                                         {"LOT_ID": lot["id"]}),
                )
                lot["status"] = "unsuccessful"
                continue

            elif last_award["status"] == "active":
                active_contracts = (
                    [a["status"] == "active" for a in tender.get("agreements")]
                    if "agreements" in tender
                    else [i["status"] == "active" and i["awardID"] == last_award["id"]
                          for i in tender.get("contracts", "")]
                )

                if any(active_contracts):
                    LOGGER.info(
                        f"Switched lot {lot['id']} of tender {tender['_id']} to complete",
                        extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_lot_complete"},
                                             {"LOT_ID": lot['id']}),
                    )
                    lot["status"] = "complete"

    def has_unanswered_tender_complaints(self, tender):
        lots = tender.get("lots")
        if lots:
            active_lots = tuple(l["id"] for l in lots if l["status"] == "active")
            result = any(
                i["status"] in self.block_tender_complaint_status
                for i in tender.get("complaints", "")
                if not i.get("relatedLot") or i["relatedLot"] in active_lots
            )
        else:
            result = any(i["status"] in self.block_tender_complaint_status
                         for i in tender.get("complaints", ""))
        return result

    @staticmethod
    def has_unanswered_tender_questions(tender):
        lots = tender.get("lots")
        if lots:
            active_lots = tuple(l["id"] for l in lots if l["status"] == "active")
            active_items = tuple(i["id"] for i in tender.get("items", "")
                                 if not i.get("relatedLot") or i["relatedLot"] in active_lots)
            result = any(
                not i.get("answer")
                for i in tender.get("questions", "")
                if i["questionOf"] == "tender"
                or i["questionOf"] == "lot" and i["relatedItem"] in active_lots
                or i["questionOf"] == "item" and i["relatedItem"] in active_items
            )
        else:
            result = any(not i.get("answer") for i in tender.get("questions", ""))
        return result

    # -- auctionPeriod.shouldStartAfter --
    def get_lot_auction_should_start_after(self, tender, lot):
        if tender.get("status") in ("active.tendering", "active.pre-qualification.stand-still", "active.auction"):
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
        if tender.get("status") in ("active.tendering", "active.pre-qualification.stand-still", "active.auction"):
            period = tender.get("auctionPeriod") or {}
            if not period.get("endDate"):
                start_date = period.get("startDate")
                if start_date:
                    number_of_bids = self.count_bids_number(tender)
                    expected_value = calc_auction_end_time(number_of_bids, dt_from_iso(start_date))
                    if get_now() > expected_value:
                        return normalize_should_start_after(expected_value, tender).isoformat()
                start_after = dt_from_iso(tender["tenderPeriod"]["endDate"])
                return normalize_should_start_after(start_after, tender).isoformat()

    def calc_auction_periods(self, tender):
        lots = tender.get("lots")
        if lots:
            for lot in lots:
                period = lot.get("auctionPeriod", {})
                # if period is None:  # auctionPeriod = null can be set by chronograph
                #     del lot["auctionPeriod"]
                #     continue

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
            # if period is None:  # auctionPeriod = null can be set by chronograph
            #     del tender["auctionPeriod"]

            start_after = self.get_auction_should_start_after(tender)
            if start_after:
                period["shouldStartAfter"] = start_after
                tender["auctionPeriod"] = period

            elif "shouldStartAfter" in period:
                del period["shouldStartAfter"]
                if not period:
                    del tender["auctionPeriod"]
    # -- auctionPeriod.shouldStartAfter --
