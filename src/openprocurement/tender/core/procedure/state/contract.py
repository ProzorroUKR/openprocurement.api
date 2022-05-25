from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.utils import (
    contracts_allow_to_complete,
    dt_from_iso,
)
from openprocurement.api.utils import (
    get_first_revision_date, get_now,
    raise_operation_error,
    context_unpack,
    to_decimal,
)
from openprocurement.api.constants import (
    UNIT_PRICE_REQUIRED_FROM,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from logging import getLogger
from decimal import Decimal, ROUND_FLOOR
from datetime import datetime


LOGGER = getLogger(__name__)


class ContractState(BaseState):
    block_complaint_status = ("answered", "pending")

    @staticmethod
    def calculate_stand_still_end(tender, lot_awards, now):
        first_revision_date = get_first_revision_date(tender)
        new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
        stand_still_ends = []
        for award in lot_awards:
            if (award.get("complaintPeriod") and
                    award.get("complaintPeriod", {}).get("endDate") and
                    (award.get("status") != "cancelled" if new_defence_complaints else True)):
                stand_still_ends.append(dt_from_iso(award["complaintPeriod"]["endDate"]))
        return max(stand_still_ends) if stand_still_ends else now

    def check_skip_award_complaint_period(self, procurementMethodRationale: str) -> bool:
        return False

    def switch_status(self, tender: dict) -> None:
        statuses = set([lot.get("status") for lot in tender.get("lots", [])])
        if statuses == {"cancelled"}:
            LOGGER.info(
                f"Switched tender {tender.get('id')} to cancelled",
                extra=context_unpack(self.request, {"MESSAGE_ID": "switched_tender_cancelled"}),
            )
            tender["status"] = "cancelled"
        elif not statuses - {"unsuccessful", "cancelled"}:
            LOGGER.info(
                f"Switched tender {tender.get('id')} to unsuccessful",
                extra=context_unpack(self.request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            tender["status"] = "unsuccessful"
        elif not statuses - {"complete", "unsuccessful", "cancelled"}:
            LOGGER.info(
                f"Switched tender {tender.get('id')} to complete",
                extra=context_unpack(self.request, {"MESSAGE_ID": "switched_tender_complete"}),
            )
            tender["status"] = "complete"

    def check_award_lot_complaints(self, tender: dict, lot_id: str, lot_awards: list, now: datetime) -> bool:
        pending_complaints = False
        for complaint in tender.get("complaints", []):
            if (complaint["status"] in self.block_complaint_status and
                    complaint.get("relatedLot") == lot_id):
                pending_complaints = True
                break

        pending_awards_complaints = False
        for award in lot_awards:
            for complaint in award.get("complaints", []):
                if complaint.get("status") in self.block_complaint_status:
                    pending_awards_complaints = True
                    break

        stand_still_end = self.calculate_stand_still_end(tender, lot_awards, now)
        skip_award_complaint_period = self.check_skip_award_complaint_period(
            tender.get("procurementMethodRationale", "")
        )
        if (
                pending_complaints
                or pending_awards_complaints
                or (now < stand_still_end and not skip_award_complaint_period)
        ):
            return False
        return True

    def check_agreements(self, tender: dict) -> bool:
        if "agreements" in tender:
            return True
        return False

    def check_lots_complaints(self, tender: dict, now: datetime) -> None:
        for lot in tender.get("lots", []):
            if lot.get("status") != "active":
                continue
            lot_awards = []
            for a in tender.get("awards", []):
                if a.get("lotID") == lot.get("id"):
                    lot_awards.append(a)
            if not lot_awards:
                continue
            last_award = lot_awards[-1]

            if not self.check_award_lot_complaints(tender, lot["id"], lot_awards, now):
                continue
            elif last_award.get("status") == "unsuccessful":
                LOGGER.info(
                    f"Switched lot {lot.get('id')} of tender {tender['_id']} to unsuccessful",
                    extra=context_unpack(self.request,
                                         {"MESSAGE_ID": "switched_lot_unsuccessful"},
                                         {"LOT_ID": lot.get("id")}),
                )
                lot["status"] = "unsuccessful"
                continue
            elif last_award.get("status") == "active":
                if self.check_agreements(tender):
                    allow_complete_lot = any([a["status"] == "active" for a in tender.get("agreements", [])])
                else:
                    contracts = [
                        contract for contract in tender.get("contracts", [])
                        if contract.get("awardID") == last_award.get("id")
                    ]
                    allow_complete_lot = contracts_allow_to_complete(contracts)
                if allow_complete_lot:
                    LOGGER.info(
                        f"Switched lot {lot.get('id')} of tender {tender['_id']} to complete",
                        extra=context_unpack(self.request,
                                             {"MESSAGE_ID": "switched_lot_complete"},
                                             {"LOT_ID": lot.get("id")}),
                    )
                    lot["status"] = "complete"
            self.switch_status(tender)

    def check_award_complaints(self, tender: dict, now: datetime) -> None:
        pending_complaints = False
        for complaint in tender.get("complaints", []):
            if complaint["status"] in self.block_complaint_status:
                pending_complaints = True
                break

        pending_awards_complaints = False
        for aw in tender.get("awards", []):
            for i in aw.get("complaints", []):
                if i.get("status") in self.block_complaint_status:
                    pending_awards_complaints = True

        stand_still_end = self.calculate_stand_still_end(tender, tender.get("awards", []), now)
        stand_still_time_expired = stand_still_end < now
        last_award_status = tender.get("awards", [])[-1].get("status") if tender.get("awards", []) else ""
        if (
                not pending_complaints
                and not pending_awards_complaints
                and stand_still_time_expired
                and last_award_status == "unsuccessful"
        ):
            LOGGER.info(
                f"Switched tender {tender['_id']} to unsuccessful",
                extra=context_unpack(self.request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            tender["status"] = "unsuccessful"

        contracts = tender.get("contracts", [])
        allow_complete_tender = contracts_allow_to_complete(contracts)
        if allow_complete_tender:
            tender["status"] = "complete"

    def check_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        now = get_now()
        if tender.get("lots"):
            for complaint in tender.get("complaints", []):
                if (complaint.get("status", "") in self.block_complaint_status and
                        complaint.get("relatedLot") is None):
                    return
            self.check_lots_complaints(tender, now)
        else:
            self.check_award_complaints(tender, now)

    def on_post(self, request):
        pass

    def validate_activate_contract(self, contract):
        items_unit_value_amount = []
        for item in contract.get("items", []):
            if item.get("unit") and item.get("quantity", None) is not None:
                if item["unit"].get("value"):
                    if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                        raise_operation_error(
                            self.request, "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                        )
                    items_unit_value_amount.append(
                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                    )

        if items_unit_value_amount and contract.get("value"):
            calculated_value = sum(items_unit_value_amount)
            if calculated_value.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR) > to_decimal(
                    contract["value"].get("amount")):
                raise_operation_error(
                    self.request, "Total amount of unit values can't be greater than contract.value.amount"
                )

        if not self.validate_tender_revision_date():
            return
        for item in contract.get("items", []):
            if item.get("unit") and item["unit"].get("value", None) is None:
                raise_operation_error(
                    self.request, "Can't activate contract while unit.value is not set for each item"
                )

    def validate_tender_revision_date(self) -> bool:
        tender = self.request.validated["tender"]
        tender_created = get_first_revision_date(tender, default=get_now())
        if tender_created < UNIT_PRICE_REQUIRED_FROM:
            return False
        return True

    def validate_contract_items(self, before: dict, after: dict) -> None:
        # TODO: Remove this logic later with adding new endpoint for items in contract
        if "items" not in after or before.get("items", []) == after.get("items", []):
            return
        items = len(before.get("items", []))
        for i in range(items):
            before_value = None
            after_value = None
            if before["items"][i].get("unit", {}).get("value", None) is not None:
                before_value = before["items"][i]["unit"].pop("value")
            if after["items"][i].get("unit", {}).get("value", None) is not None:
                after_value = after["items"][i]["unit"].pop("value")

            if before["items"][i] == after["items"][i]:
                if before_value is not None:
                    before["items"][i]["unit"]["value"] = before_value
                if after_value is not None:
                    after["items"][i]["unit"]["value"] = after_value
            else:
                raise_operation_error(
                    self.request,
                    "Updated could be only unit.value.amount in item"
                )

    def validate_contract_signing(self, after: dict):
        tender = self.request.validated["tender"]
        if self.request.validated["contract"].get("status") != "active" and "status" in after and after["status"] == "active":
            skip_complaint_period = self.check_skip_award_complaint_period(
                tender.get("procurementMethodRationale", "")
            )
            award = [a for a in tender.get("awards", []) if a.get("id") == after.get("awardID")][0]
            if not skip_complaint_period:
                stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("endDate"))
                if stand_still_end > get_now():
                    raise_operation_error(
                        self.request,
                        "Can't sign contract before stand-still period end ({})".format(stand_still_end.isoformat())
                    )
            else:
                stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("startDate"))
                if stand_still_end > get_now():
                    raise_operation_error(
                        self.request,
                        f"Can't sign contract before award activation date ({stand_still_end.isoformat()})"
                    )
            pending_complaints = [
                i
                for i in tender.get("complaints", [])
                if (i.get("status") in self.block_complaint_status and
                    i.get("relatedLot") in [None, award.get("lotID")])
            ]
            pending_awards_complaints = [
                i
                for a in tender.get("awards", [])
                for i in a.get("complaints", [])
                if (i.get("status") in self.block_complaint_status and
                    a.get("lotID") == award.get("lotID"))
            ]
            if pending_complaints or pending_awards_complaints:
                raise_operation_error(self.request, "Can't sign contract before reviewing all complaints")

    def on_patch(self, before: dict, after: dict):
        if before["status"] != "active" and after["status"] == "active":
            self.validate_activate_contract(after)
        if after["status"] == "active" and after.get("dateSigned", None) is None:
            after["dateSigned"] = get_now().isoformat()
        self.check_tender_status_method()
        super().on_patch(before, after)
