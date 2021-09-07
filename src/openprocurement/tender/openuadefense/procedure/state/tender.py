from openprocurement.api.utils import context_unpack
from openprocurement.api.constants import NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO
from openprocurement.tender.core.procedure.context import get_request, get_now
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.state.tender import TenderState
from logging import getLogger

LOGGER = getLogger(__name__)


class OpenUADefenseTenderState(TenderState):
    min_bids_number = 2
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    def awarded_events(self, tender):
        awards = tender.get("awards", [])
        if (
            awards and awards[-1]["status"] == "unsuccessful"
            and not any(c["status"] in self.block_complaint_status for c in tender.get("complaints", ""))
            and not any([c["status"] in self.block_complaint_status
                         for a in awards
                         for c in a.get("complaints", "")])
        ):
            first_revision_date = get_first_revision_date(tender)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO

            stand_still_ends = [
                a.get("complaintPeriod").get("endDate")
                for a in awards
                if a.get("complaintPeriod") and a.get("complaintPeriod").get("endDate")
                and (a["status"] != "cancelled" or not new_defence_complaints)
            ]
            if stand_still_ends:
                yield max(stand_still_ends), self.awarded_complaint_handler

    def lots_qualification_events(self, tender):
        lots = tender.get("lots")
        non_lot_complaints = (i for i in tender.get("complaints", "") if i["relatedLot"] is None)
        if not any(i["status"] in self.block_complaint_status for i in non_lot_complaints):
            first_revision_date = get_first_revision_date(tender)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO

            for lot in lots:
                if lot["status"] == "active":
                    lot_awards = [i for i in tender.get("awards", "") if i["lotID"] == lot["id"]]
                    if lot_awards and lot_awards[-1]["status"] == "unsuccessful":
                        pending_complaints = any(
                            i["status"] in self.block_complaint_status
                            for i in tender.get("complaints", "")
                            if i["relatedLot"] == lot["id"]
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
                                and (a["status"] != "cancelled" or not new_defence_complaints)
                            ]
                            if stand_still_ends:
                                yield max(stand_still_ends), self.awarded_complaint_handler

    def lots_awarded_events(self, tender):
        yield from self.lots_qualification_events(tender)

    # handlers
    def awarded_complaint_handler(self, tender):
        if tender.get("lots"):
            self.check_tender_lot_status(tender)

            statuses = {lot["status"] for lot in tender["lots"]}
            if statuses == {"cancelled"}:
                LOGGER.info(
                    f"Switched tender {tender['_id']} to cancelled",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_cancelled"}),
                )
                tender["status"] = "cancelled"
            elif not statuses.difference({"unsuccessful", "cancelled"}):
                LOGGER.info(
                    f"Switched tender {tender['_id']} to unsuccessful",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_unsuccessful"}),
                )
                tender["status"] = "unsuccessful"
            elif not statuses.difference({"complete", "unsuccessful", "cancelled"}):
                LOGGER.info(
                    f"Switched tender {tender['_id']} to complete",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_complete"}),
                )
                tender["status"] = "complete"
        else:
            now = get_now().isoformat()
            pending_complaints = any(i["status"] in self.block_complaint_status
                                     for i in tender.get("complaints", ""))
            pending_awards_complaints = any(
                i["status"] in self.block_complaint_status
                for a in tender.get("awards", "")
                for i in a.get("complaints", "")
            )
            first_revision_date = get_first_revision_date(tender)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
            stand_still_ends = [
                a["complaintPeriod"]["endDate"]
                for a in tender.get("awards", "")
                if (
                        a.get("complaintPeriod", {}).get("endDate")
                        and (a["status"] != "cancelled" if new_defence_complaints else True)
                )
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
                LOGGER.info(
                    f"Switched tender {tender['_id']} to unsuccessful",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_unsuccessful"}),
                )
                tender["status"] = "unsuccessful"

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
                tender["status"] = "complete"

    # utils
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
            first_revision_date = get_first_revision_date(tender)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
            stand_still_ends = [
                a["complaintPeriod"]["endDate"]
                for a in lot_awards
                if (
                        a.get("complaintPeriod", {}).get("endDate")
                        and (a["status"] != "cancelled" if new_defence_complaints else True)
                )
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

    def check_bids_number(self, tender):
        if tender.get("lots"):
            max_bid_number = 0
            for lot in tender["lots"]:
                bid_number = self.count_lot_bids_number(tender, lot["id"])
                max_bid_number = max(max_bid_number, bid_number)
                if bid_number < self.min_bids_number:
                    if lot.get("auctionPeriod", {}).get("startDate"):
                        del lot["auctionPeriod"]["startDate"]
                        if not lot["auctionPeriod"]:
                            del lot["auctionPeriod"]

                    if bid_number == 0 and lot["status"] == "active":
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

            if max_bid_number == 1:
                self.add_next_award(get_request())

            # should be moved to tender_status_check ?
            if not set(i["status"] for i in tender["lots"]).difference({"unsuccessful", "cancelled"}):
                tender["status"] = "unsuccessful"
        else:
            bid_number = self.count_bids_number(tender)
            if bid_number < self.min_bids_number:
                if tender.get("auctionPeriod", {}).get("startDate"):
                    del tender["auctionPeriod"]["startDate"]
                    if not tender["auctionPeriod"]:
                        del tender["auctionPeriod"]

                if bid_number == 1:
                    self.add_next_award(get_request())
                else:
                    tender["status"] = "unsuccessful"
