from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_tender, get_request, get_award
from openprocurement.tender.core.procedure.utils import (
    get_contracts_values_related_to_patched_contract,
    contracts_allow_to_complete,
    dt_from_iso,
)
from openprocurement.api.context import get_now
from openprocurement.api.validation import OPERATIONS
from openprocurement.api.utils import (
    get_first_revision_date,
    raise_operation_error,
    context_unpack,
    to_decimal,
)
from openprocurement.api.constants import (
    UNIT_PRICE_REQUIRED_FROM,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.tender.core.constants import AMOUNT_NET_COEF
from schematics.types import BaseType
from itertools import zip_longest
from logging import getLogger
from decimal import Decimal, ROUND_FLOOR, ROUND_UP
from datetime import datetime


LOGGER = getLogger(__name__)


class ContractStateMixing:
    allowed_statuses_from = ("pending", "pending.winner-signing")
    allowed_statuses_to = ("active", "pending", "pending.winner-signing")

    set_object_status: callable  # from BaseState
    block_complaint_status: tuple  # from TenderState
    check_skip_award_complaint_period: callable  # from TenderState
    validate_cancellation_blocks: callable  # from TenderState

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

    def switch_status(self, tender: dict) -> None:
        statuses = set([lot.get("status") for lot in tender.get("lots", [])])
        if statuses == {"cancelled"}:
            LOGGER.info(
                f"Switched tender {tender.get('id')} to cancelled",
                extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_cancelled"}),
            )
            self.set_object_status(tender, "cancelled")
        elif not statuses - {"unsuccessful", "cancelled"}:
            LOGGER.info(
                f"Switched tender {tender.get('id')} to unsuccessful",
                extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            self.set_object_status(tender, "unsuccessful")
        elif not statuses - {"complete", "unsuccessful", "cancelled"}:
            LOGGER.info(
                f"Switched tender {tender.get('id')} to complete",
                extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_complete"}),
            )
            self.set_object_status(tender, "complete")

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
        skip_award_complaint_period = self.check_skip_award_complaint_period()
        if (
            pending_complaints
            or pending_awards_complaints
            or (now < stand_still_end and not skip_award_complaint_period)
        ):
            return False
        return True

    def check_agreements(self, tender: dict) -> bool:
        return "agreements" in tender

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
                    extra=context_unpack(get_request(),
                                         {"MESSAGE_ID": "switched_lot_unsuccessful"},
                                         {"LOT_ID": lot.get("id")}),
                )
                self.set_object_status(lot, "unsuccessful")
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
                        extra=context_unpack(get_request(),
                                             {"MESSAGE_ID": "switched_lot_complete"},
                                             {"LOT_ID": lot.get("id")}),
                    )
                    self.set_object_status(lot, "complete")
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
                extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            self.set_object_status(tender, "unsuccessful")

        contracts = tender.get("contracts", [])
        allow_complete_tender = contracts_allow_to_complete(contracts)
        if allow_complete_tender:
            self.set_object_status(tender, "complete")

    def check_tender_status_method(self) -> None:
        tender = get_tender()
        now = get_now()
        if tender.get("lots"):
            for complaint in tender.get("complaints", []):
                if (complaint.get("status", "") in self.block_complaint_status and
                        complaint.get("relatedLot") is None):
                    return
            self.check_lots_complaints(tender, now)
        else:
            self.check_award_complaints(tender, now)

    def contract_on_post(self, request):
        pass

    def validate_activate_contract(self, contract):
        items_unit_value_amount = []
        for item in contract.get("items", []):
            if item.get("unit") and item.get("quantity", None) is not None:
                if item["unit"].get("value"):
                    if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                        raise_operation_error(
                            get_request(), "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                        )
                    items_unit_value_amount.append(
                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                    )

        if items_unit_value_amount and contract.get("value"):
            calculated_value = sum(items_unit_value_amount)
            if calculated_value.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR) > to_decimal(
                    contract["value"].get("amount")):
                raise_operation_error(
                    get_request(), "Total amount of unit values can't be greater than contract.value.amount"
                )

        if get_first_revision_date(get_tender()) >= UNIT_PRICE_REQUIRED_FROM:
            for item in contract.get("items", []):
                if item.get("unit") and item["unit"].get("value", None) is None:
                    raise_operation_error(
                        get_request(), "Can't activate contract while unit.value is not set for each item"
                    )

    def validate_contract_items(self, before: dict, after: dict) -> None:
        # TODO: Remove this logic later with adding new endpoint for items in contract
        items_before = before.get("items", [])
        items_after = after.get("items", [])
        for item_before, item_after in zip_longest(items_before, items_after):
            if None in (item_before, item_after):
                raise_operation_error(
                    get_request(),
                    "Can't change items list length"
                )
            else:
                for k in item_before.keys() | item_after.keys():
                    before, after = item_before.get(k), item_after.get(k)
                    if not before and not after:  # [] or None check
                        continue

                    if k == "unit":
                        before = {k: v for k, v in (before or {}).items() if k != "value"}
                        after = {k: v for k, v in (after or {}).items() if k != "value"}

                    if before != after:
                        raise_operation_error(
                            get_request(),
                            "Updated could be only unit.value.amount in item"
                        )

    def validate_contract_signing(self, before: dict,  after: dict):
        tender = get_tender()
        if before.get("status") != "active" and after.get("status") == "active":
            award = [a for a in tender.get("awards", []) if a.get("id") == after.get("awardID")][0]
            self._validate_contract_signing_before_due_date(award)
            self._validate_contract_signing_with_pending_complaints(award)

    def _validate_contract_signing_before_due_date(self, award: dict):
        skip_complaint_period = self.check_skip_award_complaint_period()

        if not skip_complaint_period:
            stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("endDate"))
            if stand_still_end > get_now():
                raise_operation_error(
                    get_request(),
                    "Can't sign contract before stand-still period end ({})".format(stand_still_end.isoformat())
                )
        else:
            stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("startDate"))
            if stand_still_end > get_now():
                raise_operation_error(
                    get_request(),
                    f"Can't sign contract before award activation date ({stand_still_end.isoformat()})"
                )

    def _validate_contract_signing_with_pending_complaints(self, award: dict):
        tender = get_tender()
        pending_complaints = [
            i
            for i in tender.get("complaints", [])
            if (i.get("status") in self.block_complaint_status and
                i.get("relatedLot") in (None, award.get("lotID")))
        ]
        pending_awards_complaints = [
            i
            for a in tender.get("awards", [])
            for i in a.get("complaints", [])
            if (i.get("status") in self.block_complaint_status and
                a.get("lotID") == award.get("lotID"))
        ]
        if pending_complaints or pending_awards_complaints:
            raise_operation_error(get_request(), "Can't sign contract before reviewing all complaints")


    def validate_contract_patch(self, request, before: dict, after: dict):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))

    def contract_on_patch(self, before: dict, after: dict):
        if before["status"] != after["status"]:
            self.contract_status_up(before["status"], after["status"], after)
        if before["status"] != "active" and after["status"] == "active":
            self.validate_activate_contract(after)
        if after["status"] == "active" and after.get("dateSigned", None) is None:
            after["dateSigned"] = get_now().isoformat()
        if after.get("value", {}) != before.get("value", {}):
            self.synchronize_items_unit_value(after)
        self.check_tender_status_method()

    def contract_status_up(self, before, after, data):
        assert before != after, "Statuses must be different"
        data["date"] = get_now().isoformat()

    def synchronize_items_unit_value(self, contract):
        valueAddedTaxIncluded = contract["value"]["valueAddedTaxIncluded"]
        currency = contract["value"]["currency"]
        for item in contract.get("items", ""):
            if item.get("unit"):
                if item["unit"].get("value"):
                    item["unit"]["value"].update(
                        {
                            "valueAddedTaxIncluded": valueAddedTaxIncluded,
                            "currency": currency,
                        }
                    )

    # validators
    def validate_contract_post(self, request, tender, contract):
        self.validate_contract_operation_not_in_allowed_status(request, tender)

    def validate_contract_patch(self, request, before, after):
        tender = get_tender()
        self.validate_contract_operation_not_in_allowed_status(request, tender)
        self.validate_update_contract_only_for_active_lots(request, tender, before)
        self.validate_update_contract_status_by_supplier(request, before, after)
        self.validate_update_contract_status(request, tender, before, after)
        self.validate_contract_update_with_accepted_complaint(request, tender, before)  # openua
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_with_award(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)

    @staticmethod
    def validate_contract_operation_not_in_allowed_status(request, tender):
        status = tender["status"]
        if status not in ("active.qualification", "active.awarded"):
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} contract in current ({status}) tender status"
            )

    @staticmethod
    def validate_update_contract_only_for_active_lots(request, tender, contract):
        award_lot_ids = []
        for award in tender.get("awards", []):
            if award.get("id") == contract.get("awardID"):
                award_lot_ids.append(award.get("lotID"))

        for lot in tender.get("lots", []):
            if lot.get("status") != "active" and lot.get("id") in award_lot_ids:
                raise_operation_error(request, "Can update contract only in active lot status")

    @staticmethod
    def validate_update_contract_status_by_supplier(request, before, after):
        if request.authenticated_role == "contract_supplier":
            if (
                before["status"] != after["status"]
                and after["status"] != "pending"
                or before["status"] != "pending.winner-signing"
            ):
                raise_operation_error(request, "Supplier can change status to `pending`")

    @classmethod
    def validate_update_contract_status(cls, request, tender, before, after):
        allowed_statuses_to = cls.allowed_statuses_to
        # Allow change contract status to cancelled for multi buyers tenders
        multi_contracts = len(tender.get("buyers", [])) > 1
        if multi_contracts:
            allowed_statuses_to += ("cancelled",)

        # Validate status change
        current_status = before["status"]
        new_status = after["status"]
        if (
            current_status != new_status
            and (
                current_status not in cls.allowed_statuses_from
                or new_status not in allowed_statuses_to
            )
        ):
            raise_operation_error(request, "Can't update contract status")

        not_cancelled_contracts_count = sum(
            1 for contract in tender.get("contracts", [])
            if (
                    contract.get("status") != "cancelled"
                    and contract.get("awardID") == request.validated["contract"]["awardID"]
            )
        )
        if multi_contracts and new_status == "cancelled" and not_cancelled_contracts_count == 1:
            raise_operation_error(
                request,
                f"Can't update contract status from {current_status} to {new_status} "
                f"for last not cancelled contract. Cancel award instead."
            )

    @staticmethod
    def validate_contract_update_with_accepted_complaint(request, tender, contract):
        award_id = contract.get("awardID", "")
        for award in tender.get("awards", []):
            if award["id"] == award_id:
                for complaint in award.get("complaints", []):
                    if complaint.get("status", "") == "accepted":
                        raise_operation_error(request, "Can't update contract with accepted complaint")

    @staticmethod
    def validate_update_contract_value(request, before, after):
        value = after.get("value")
        if value:
            field = before.get("value")
            if field and value.get("currency") != field.get("currency"):
                raise_operation_error(request, "Can't update currency for contract value", name="value")

    @staticmethod
    def validate_update_contract_value_net_required(request, before, after):
        value = after.get("value")
        if value is not None and before.get("status") != after.get("status"):
            contract_amount_net = value.get("amountNet")
            if contract_amount_net is None:
                raise_operation_error(
                    request,
                    {"amountNet": BaseType.MESSAGES["required"]},
                    status=422,
                    name="value"
                )

    @staticmethod
    def validate_update_contract_value_with_award(request, before, after):
        value = after.get("value")
        if value and (
            before.get("value") != after.get("value") or
            before.get("status") != after.get("status")
        ):

            award = [
                award for award in request.validated["tender"].get("awards", [])
                if award.get("id") == request.validated["contract"].get("awardID")
            ][0]

            _contracts_values = get_contracts_values_related_to_patched_contract(
                request.validated["tender"].get("contracts"),
                request.validated["contract"]["id"], value,
                request.validated["contract"].get("awardID")
            )
            amount = sum([to_decimal(value.get("amount", 0)) for value in _contracts_values])
            amount_net = sum([to_decimal(value.get("amountNet", 0)) for value in _contracts_values])
            tax_included = value.get("valueAddedTaxIncluded")
            if tax_included:
                if award.get("value", {}).get("valueAddedTaxIncluded"):
                    if amount > to_decimal(award.get("value", {}).get("amount")):
                        raise_operation_error(
                            request, "Amount should be less or equal to awarded amount", name="value"
                        )
                else:
                    if amount_net > to_decimal(award.get("value", {}).get("amount")):
                        raise_operation_error(
                            request, "AmountNet should be less or equal to awarded amount", name="value"
                        )
            else:
                if amount > to_decimal(award.get("value", {}).get("amount")):
                    raise_operation_error(
                        request, "Amount should be less or equal to awarded amount", name="value"
                    )

    @staticmethod
    def validate_update_contract_value_amount(request, before, after):
        value = after.get("value")
        if value and (
            before.get("value") != after.get("value") or
            before.get("status") != after.get("status")
        ):
            amount = to_decimal(value.get("amount") or 0)
            amount_net = to_decimal(value.get("amountNet") or 0)
            tax_included = value.get("valueAddedTaxIncluded")

            if not (amount == 0 and amount_net == 0):
                if tax_included:
                    amount_max = (amount_net * AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_UP)
                    if (amount < amount_net or amount > amount_max):
                        raise_operation_error(
                            request,
                            f"Amount should be equal or greater than amountNet and differ by "
                            f"no more than {AMOUNT_NET_COEF * 100 - 100}%",
                            name="value",
                        )
                else:
                    if amount != amount_net:
                        raise_operation_error(request, "Amount and amountNet should be equal", name="value")

class ContractState(ContractStateMixing, TenderState):
    pass
