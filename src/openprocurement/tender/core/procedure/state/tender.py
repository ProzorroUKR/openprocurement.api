from openprocurement.api.utils import context_unpack, raise_operation_error
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.context import get_now, get_request, since_2020_rules
from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.state.chronograph import ChronographEventsMixing
from openprocurement.tender.core.procedure.state.auction import BaseShouldStartAfterMixing
from logging import getLogger


LOGGER = getLogger(__name__)


class TenderState(BaseShouldStartAfterMixing, TenderStateAwardingMixing, ChronographEventsMixing, BaseState):
    min_bids_number = 2
    active_bid_statuses = ("active",)  # are you intrigued ?
    # used by bid counting methods

    block_complaint_status = ("answered", "pending")
    block_tender_complaint_status = ("claim", "pending", "accepted", "satisfied", "stopping")
    # tender can't proceed to "active.auction" until has a tender.complaints in one of statuses above
    unsuccessful_statuses = ("cancelled", "unsuccessful")
    terminated_statuses = ("complete", "unsuccessful", "cancelled", "draft.unsuccessful")

    contract_model = Contract

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        data["date"] = get_now().isoformat()

        # TODO: redesign auction planning
        if after in self.unsuccessful_statuses:
            self.remove_all_auction_periods(data)

    def always(self, data):
        super().always(data)
        self.update_next_check(data)
        self.calc_auction_periods(data)

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
                    self.remove_auction_period(lot)

                    if lot.get("status") == "active":  # defense procedures doesn't have lot status, for ex
                        self.set_object_status(lot, "unsuccessful")
                        self.set_lot_values_unsuccessful(tender.get("bids"), lot["id"])

            active_lots = {l["id"] for l in tender["lots"] if l["status"] == "active"}
            # set bids unsuccessful
            for bid in tender.get("bids", ""):
                if not any(lv["relatedLot"] in active_lots
                           for lv in bid.get("lotValues", "")):
                    if bid.get("status", "active") in self.active_bid_statuses:
                        bid["status"] = "unsuccessful"

            # should be moved to tender_status_check ?
            if not set(i["status"] for i in tender["lots"]).difference({"unsuccessful", "cancelled"}):
                self.get_change_tender_status_handler("unsuccessful")(tender)
        else:
            bid_number = self.count_bids_number(tender)
            if bid_number < self.min_bids_number:
                self.remove_auction_period(tender)

                for bid in tender.get("bids", ""):
                    if bid.get("status", "active") in self.active_bid_statuses:
                        bid["status"] = "unsuccessful"

                self.get_change_tender_status_handler("unsuccessful")(tender)

    def set_lot_values_unsuccessful(self, bids, lot_id):
        # for procedures where lotValues have "status" field (openeu, competitive_dialogue, cfaua, )
        for bid in bids or "":
            for lot_value in bid.get("lotValues", ""):
                if "status" in lot_value:
                    if lot_value["relatedLot"] == lot_id:
                        self.set_object_status(lot_value, "unsuccessful")

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
            if bid.get("status", "active") in cls.active_bid_statuses:
                for lot_value in bid.get("lotValues", ""):
                    if lot_value.get("status", "active") in cls.active_bid_statuses and lot_value["relatedLot"] == lot_id:
                        count += 1
                        break  # proceed to the next bid check
        return count

    @staticmethod
    def check_skip_award_complaint_period():
        return False

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
            skip_award_complaint_period = self.check_skip_award_complaint_period()
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
                self.set_object_status(lot, "unsuccessful")
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
                    self.set_object_status(lot, "complete")

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

    def remove_all_auction_periods(self, tender):
        self.remove_auction_period(tender)
        for lot in tender.get("lots", ""):
            self.remove_auction_period(lot)

    @staticmethod
    def remove_auction_period(obj):
        auction_period = obj.get("auctionPeriod")
        if auction_period and "endDate" not in auction_period:
            del obj["auctionPeriod"]

    def calc_tender_values(self, tender: dict) -> None:
        if tender.get("lots"):
            self.calc_tender_value(tender)
            self.calc_tender_guarantee(tender)
            self.calc_tender_minimal_step(tender)

    @staticmethod
    def calc_tender_value(tender: dict) -> None:
        tender["value"] = {
            "amount": sum(i["value"]["amount"] for i in tender.get("lots", "") if i.get("value")),
            "currency": tender["value"]["currency"],
            "valueAddedTaxIncluded": tender["value"]["valueAddedTaxIncluded"]
        }

    @staticmethod
    def calc_tender_guarantee(tender: dict) -> None:
        lots_amount = [i["guarantee"]["amount"] for i in tender.get("lots", "") if i.get("guarantee")]
        if not lots_amount:
            return
        guarantee = {"amount": sum(lots_amount)}
        lots_currency = [i["guarantee"]["currency"] for i in tender["lots"] if i.get("guarantee")]
        guarantee["currency"] = lots_currency[0] if lots_currency else None
        if tender.get("guarantee"):
            guarantee["currency"] = tender["guarantee"]["currency"]
        tender["guarantee"] = guarantee

    @staticmethod
    def calc_tender_minimal_step(tender: dict) -> None:
        tender["minimalStep"] = {
            "amount": min(i["minimalStep"]["amount"] for i in tender.get("lots", "") if i.get("minimalStep")),
            "currency": tender["minimalStep"]["currency"],
            "valueAddedTaxIncluded": tender["minimalStep"]["valueAddedTaxIncluded"],
        }

    @staticmethod
    def cancellation_blocks_tender(tender, lot_id=None):
        """
        A pending cancellation stop the tender process
        until the either tender is cancelled or cancellation is cancelled 🤯
        :param tender:
        :param lot_id: if passed, then other lot cancellations are not considered
        :return:
        """
        if not since_2020_rules() \
           or tender["procurementMethodType"] in ("belowThreshold", "closeFrameworkAgreementSelectionUA"):
            return False

        related_cancellations = [
            c for c in tender.get("cancellations", "")
            if lot_id is None  # we don't care of lot
            or c.get("relatedLot") in (None, lot_id)  # it's tender or this lot cancellation
        ]

        if any(
            i["status"] == "pending"
            for i in related_cancellations
        ):
            return True

        # unsuccessful also blocks tender
        accept_tender = all(
            any(complaint["status"] == "resolved" for complaint in c.get("complaints"))
            for c in related_cancellations
            if c["status"] == "unsuccessful" and c.get("complaints")
        )
        return not accept_tender

    def validate_cancellation_blocks(self, request, tender, lot_id=None):
        if self.cancellation_blocks_tender(tender, lot_id):
            raise_operation_error(request, "Can't perform action due to a pending cancellation")
