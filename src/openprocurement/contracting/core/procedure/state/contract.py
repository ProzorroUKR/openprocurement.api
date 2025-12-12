import hashlib
import json
from datetime import datetime, timedelta
from decimal import ROUND_UP, Decimal
from itertools import zip_longest
from logging import getLogger
from typing import Callable, Optional

from pyramid.request import Request
from schematics.types import BaseType

from openprocurement.api.constants_env import (
    ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM,
    MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
    RELEASE_2020_04_19,
    UNIT_PRICE_REQUIRED_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_request, get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import get_items, parse_date, to_decimal
from openprocurement.api.utils import (
    calculate_full_date,
    context_unpack,
    get_first_revision_date,
    get_now,
    raise_operation_error,
)
from openprocurement.api.validation import OPERATIONS
from openprocurement.contracting.core.procedure.utils import (
    is_bid_owner,
    is_contract_owner,
)
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    IgnoredClaimMixing,
)
from openprocurement.tender.core.constants import AMOUNT_NET_COEF
from openprocurement.tender.core.procedure.cancelling import CancellationBlockMixing
from openprocurement.tender.core.procedure.state.utils import awarding_is_unsuccessful
from openprocurement.tender.core.procedure.utils import (
    check_is_contract_waiting_for_inspector_approve,
    contracts_allow_to_complete,
    dt_from_iso,
    is_multi_currency_tender,
    set_mode_test_titles,
    tender_created_after,
    tender_created_in,
)
from openprocurement.tender.core.procedure.validation import (
    validate_items_unit_amount,
    validate_milestone_duration_days,
    validate_milestone_sums,
    validate_milestones_sequence_number,
)
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL

LOGGER = getLogger(__name__)


class ContractStateMixing:
    request: Request
    block_complaint_status: tuple

    set_object_status: Callable
    check_skip_award_complaint_period: Callable

    @staticmethod
    def calculate_stand_still_end(tender, lot_awards, now):
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        stand_still_ends = []
        for award in lot_awards:
            if (
                award.get("complaintPeriod")
                and award.get("complaintPeriod", {}).get("endDate")
                and (award.get("status") != "cancelled" if new_defence_complaints else True)
            ):
                stand_still_ends.append(dt_from_iso(award["complaintPeriod"]["endDate"]))
        return max(stand_still_ends) if stand_still_ends else now

    def switch_status(self, tender: dict) -> None:
        statuses = {lot.get("status") for lot in tender.get("lots", [])}
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
            if complaint["status"] in self.block_complaint_status and complaint.get("relatedLot") == lot_id:
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

    def check_lots_complaints(self, tender: dict, now: datetime) -> None:
        awarding_order_enabled = tender["config"]["hasAwardingOrder"]
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
            awards_statuses = {award["status"] for award in lot_awards}

            if not self.check_award_lot_complaints(tender, lot["id"], lot_awards, now):
                continue
            elif awarding_is_unsuccessful(lot_awards):
                LOGGER.info(
                    f"Switched lot {lot.get('id')} of tender {tender['_id']} to unsuccessful",
                    extra=context_unpack(
                        get_request(),
                        {"MESSAGE_ID": "switched_lot_unsuccessful"},
                        {"LOT_ID": lot.get("id")},
                    ),
                )
                self.set_object_status(lot, "unsuccessful")
                continue
            elif (awarding_order_enabled and last_award["status"] == "active") or (
                awarding_order_enabled is False and awards_statuses.intersection({"active"})
            ):
                if (
                    "agreements" in tender
                    and tender["config"]["hasPreSelectionAgreement"] is False  # tender produces agreements
                ):
                    allow_complete_lot = any(a["status"] == "active" for a in tender.get("agreements", []))
                else:
                    if awarding_order_enabled is False:
                        active_award_ids = {award["id"] for award in lot_awards if award["status"] == "active"}
                        contracts = [
                            contract
                            for contract in tender.get("contracts", [])
                            if contract.get("awardID") in active_award_ids
                        ]
                    else:
                        contracts = [
                            contract
                            for contract in tender.get("contracts", [])
                            if contract.get("awardID") == last_award.get("id")
                        ]
                    allow_complete_lot = contracts_allow_to_complete(contracts)
                if allow_complete_lot:
                    LOGGER.info(
                        f"Switched lot {lot.get('id')} of tender {tender['_id']} to complete",
                        extra=context_unpack(
                            get_request(),
                            {"MESSAGE_ID": "switched_lot_complete"},
                            {"LOT_ID": lot.get("id")},
                        ),
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
        awards = tender.get("awards", [])
        if (
            not pending_complaints
            and not pending_awards_complaints
            and stand_still_time_expired
            and awarding_is_unsuccessful(awards)
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
        now = get_request_now()
        if tender.get("lots"):
            for complaint in tender.get("complaints", []):
                if complaint.get("status", "") in self.block_complaint_status and complaint.get("relatedLot") is None:
                    return
            self.check_lots_complaints(tender, now)
        else:
            self.check_award_complaints(tender, now)

    def contract_on_post(self, data):
        pass

    def validate_activate_contract(self, contract):
        items_unit_value_amount = []
        for item in contract.get("items", []):
            if item.get("unit") and item.get("quantity", None) is not None:
                if item["unit"].get("value"):
                    if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                        raise_operation_error(
                            get_request(),
                            "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0",
                            status=422,
                        )
                    items_unit_value_amount.append(
                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                    )

        validate_items_unit_amount(items_unit_value_amount, contract)

        if tender_created_after(UNIT_PRICE_REQUIRED_FROM):
            for item in contract.get("items", []):
                if item.get("unit") and item["unit"].get("value", None) is None:
                    raise_operation_error(
                        get_request(),
                        "Can't activate contract while unit.value is not set for each item",
                    )

    def validate_contract_signing(self, before: dict, after: dict):
        tender = get_tender()
        if before.get("status") != "active" and after.get("status") == "active":
            award = [a for a in tender.get("awards", []) if a.get("id") == after.get("awardID")][0]
            self._validate_contract_signing_before_due_date(award)
            self._validate_contract_signing_with_pending_complaints(award)

    def _validate_contract_signing_before_due_date(self, award: dict):
        skip_complaint_period = self.check_skip_award_complaint_period()

        if not skip_complaint_period:
            stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("endDate"))
            if stand_still_end > get_request_now():
                raise_operation_error(
                    get_request(),
                    "Can't sign contract before stand-still period end ({})".format(stand_still_end.isoformat()),
                )
        else:
            if complaint_period_start := award.get("complaintPeriod", {}).get("startDate"):
                stand_still_end = dt_from_iso(complaint_period_start)
                if stand_still_end > get_request_now():
                    raise_operation_error(
                        get_request(),
                        f"Can't sign contract before award activation date ({stand_still_end.isoformat()})",
                    )

    def _validate_contract_signing_with_pending_complaints(self, award: dict):
        tender = get_tender()
        pending_complaints = [
            i
            for i in tender.get("complaints", [])
            if (i.get("status") in self.block_complaint_status and i.get("relatedLot") in (None, award.get("lotID")))
        ]
        pending_awards_complaints = [
            i
            for a in tender.get("awards", [])
            for i in a.get("complaints", [])
            if (i.get("status") in self.block_complaint_status and a.get("lotID") == award.get("lotID"))
        ]
        if pending_complaints or pending_awards_complaints:
            raise_operation_error(get_request(), "Can't sign contract before reviewing all complaints")

    def contract_on_patch(self, before: dict, after: dict):
        if before["status"] != after["status"]:
            self.contract_status_up(before["status"], after["status"], after)
        if before["status"] != "active" and after["status"] == "active":
            self.validate_activate_contract(after)
            self.validate_activate_contract_with_review_request(
                self.request,
                self.request.validated["tender"],
                after,
                self.request.validated["award"].get("lotID"),
            )
        if after["status"] == "active" and after.get("dateSigned", None) is None:
            after["dateSigned"] = get_request_now().isoformat()
        if after.get("value", {}) != before.get("value", {}):
            self.synchronize_items_unit_value(after)
        self.check_tender_status_method()

    def contract_status_up(self, before, after, data):
        assert before != after, "Statuses must be different"
        data["date"] = get_request_now().isoformat()

    def synchronize_items_unit_value(self, contract, value=None):
        if contract.get("value"):
            value_data = contract["value"]
        elif value is not None:
            value_data = value
        else:
            return
        valueAddedTaxIncluded = value_data["valueAddedTaxIncluded"]
        currency = value_data["currency"]
        for item in contract.get("items", ""):
            if item.get("unit"):
                if item["unit"].get("value"):
                    if tender_created_after(ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM):
                        item["unit"]["value"]["valueAddedTaxIncluded"] = False  # CS-18784 must be always False
                    else:
                        item["unit"]["value"]["valueAddedTaxIncluded"] = valueAddedTaxIncluded
                    if not is_multi_currency_tender(check_funders=True):
                        item["unit"]["value"]["currency"] = currency

    # validators
    def validate_contract_post(self, request, tender, contract):
        self.validate_contract_operation_not_in_allowed_status(request, tender)

    @staticmethod
    def validate_contract_operation_not_in_allowed_status(request, tender):
        status = tender["status"]
        if status not in ("active.qualification", "active.awarded"):
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} contract in current ({status}) tender status",
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
    def validate_update_contract_value_amount(request, before, after, name="value"):
        value = after.get(name)
        if value and (before.get(name) != after.get(name) or before.get("status") != after.get("status", "active")):
            amount = to_decimal(value.get("amount") or 0)
            amount_net = to_decimal(value.get("amountNet") or 0)
            tax_included = value.get("valueAddedTaxIncluded")

            if not (amount == 0 and amount_net == 0):
                if tax_included:
                    amount_max = (amount_net * AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_UP)
                    if amount < amount_net or amount > amount_max:
                        raise_operation_error(
                            request,
                            f"Amount should be equal or greater than amountNet and differ by "
                            f"no more than {AMOUNT_NET_COEF * 100 - 100}%",
                            name="value",
                        )
                else:
                    if amount != amount_net:
                        raise_operation_error(
                            request,
                            "Amount and amountNet should be equal",
                            name="value",
                        )

    @staticmethod
    def validate_activate_contract_with_review_request(
        request, tender: dict, after: dict, lot_id: Optional[str] = None
    ) -> None:
        if check_is_contract_waiting_for_inspector_approve(tender, lot_id):
            raise_operation_error(
                request,
                f"Can't update contract to {after['status']} till inspector approve",
            )


class ESCOContractStateMixing:
    value_attrs = (
        "amount",
        "amount_escp",
        "amountPerformance",
        "amountPerformance_npv",
        "yearlyPaymentsPercentage",
        "annualCostsReduction",
        "contractDuration",
        "currency",
    )

    @classmethod
    def validate_update_contract_value_esco(cls, request, before, after, convert_annual_costs=True):
        value = after.get("value")
        if value:
            for ro_attr in cls.value_attrs:
                field = before.get("value")
                if convert_annual_costs and ro_attr == "annualCostsReduction" and field.get(ro_attr):
                    # This made because of not everywhere DecimalType is new
                    # and when old model validate whole tender, value here become
                    # form 1E+2, but in request.validated['data'] we get '100'
                    field[ro_attr] = ["{:f}".format(to_decimal(i)) for i in field[ro_attr]]
                if field:
                    passed = value.get(ro_attr)
                    actual = field.get(ro_attr)
                    if isinstance(passed, Decimal):
                        actual = to_decimal(actual)
                    if ro_attr == "annualCostsReduction":
                        # if compare strings equality ['9.0', '1.0',...] and ['9.00', '1.00', ...] and ['9', '1', ...]
                        # these cases aren't equal
                        # that's why we should convert them to decimal
                        passed = [to_decimal(i) for i in passed]
                        actual = [to_decimal(i) for i in actual]
                    if passed != actual:
                        raise_operation_error(
                            request,
                            f"Can't update {ro_attr} for contract value",
                            name="value",
                        )


class CFASelectionContractStateMixing:
    request: Request
    set_object_status: Callable

    def check_cfaseslectionua_agreements(self, tender: dict) -> bool:
        return False

    def check_cfaseslectionua_award_lot_complaints(
        self, tender: dict, lot_id: str, lot_awards: list, now: datetime
    ) -> bool:
        return True

    def check_cfaseslectionua_award_complaints(self, tender: dict, now: datetime) -> None:
        last_award_status = tender.get("awards", [])[-1].get("status") if tender.get("awards", []) else ""
        if last_award_status == "unsuccessful":
            LOGGER.info(
                f"Switched tender {tender['id']} to unsuccessful",
                extra=context_unpack(self.request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            self.set_object_status(tender, "unsuccessful")

        contracts = tender.get("contracts", [])
        allow_complete_tender = contracts_allow_to_complete(contracts)
        if allow_complete_tender:
            self.set_object_status(tender, "complete")


class LimitedContractStateMixing:
    request: Request

    set_object_status: Callable

    block_complaint_status: tuple

    def check_contracts_statuses(self, tender):
        active_contracts = False
        pending_contracts = False

        for contract in tender.get("contracts", []):
            if contract["status"] == "active":
                active_contracts = True
            elif contract["status"] == "pending":
                pending_contracts = True

        if tender.get("contracts", []) and active_contracts and not pending_contracts:
            self.set_object_status(tender, "complete")

    def check_contracts_lot_statuses(self, tender: dict) -> None:
        now = get_request_now()
        for lot in tender["lots"]:
            if lot["status"] != "active":
                continue
            lot_awards = [i for i in tender.get("awards", []) if i.get("lotID") == lot["id"]]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_awards_complaints = any(
                [i["status"] in ["claim", "answered", "pending"] for a in lot_awards for i in a.get("complaints", [])]
            )
            stand_still_end = max(
                (
                    dt_from_iso(award["complaintPeriod"]["endDate"])
                    if award.get("complaintPeriod", {}) and award["complaintPeriod"].get("endDate")
                    else now
                )
                for award in lot_awards
            )
            if pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award["status"] == "unsuccessful":
                self.set_object_status(lot, "unsuccessful")
                continue
            elif last_award["status"] == "active" and any(
                [
                    contract["status"] == "active" and contract.get("awardID") == last_award["id"]
                    for contract in tender.get("contracts", [])
                ]
            ):
                self.set_object_status(lot, "complete")
        statuses = {lot["status"] for lot in tender.get("lots", [])}

        if statuses == {"cancelled"}:
            self.set_object_status(tender, "cancelled")
        elif not statuses - {"unsuccessful", "cancelled"}:
            self.set_object_status(tender, "unsuccessful")
        elif not statuses - {"complete", "unsuccessful", "cancelled"}:
            self.set_object_status(tender, "complete")

    def validate_limited_contract_with_cancellations(self, before: dict, after: dict) -> None:
        tender = get_tender()
        new_rules = get_first_revision_date(tender, default=get_request_now()) > RELEASE_2020_04_19

        if before.get("status") != "active" and after.get("status") == "active":
            award_id = self.request.validated["contract"].get("awardID")
            award = [a for a in tender.get("awards") if a["id"] == award_id][0]
            lot_id = award.get("lotID")

            new_rules_block_complaints = any(
                complaint["status"] in self.block_complaint_status and cancellation.get("relatedLot") == lot_id
                for cancellation in tender.get("cancellations", "")
                for complaint in cancellation.get("complaints", "")
            )

            if new_rules and new_rules_block_complaints:
                raise_operation_error(self.request, "Can't sign contract before reviewing all complaints")

    def check_reporting_tender_status_method(self) -> None:
        self.check_contracts_statuses(self.request.validated["tender"])

    def check_negotiation_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        if tender.get("lots"):
            self.check_contracts_lot_statuses(tender)
        else:
            self.check_contracts_statuses(tender)


class ContractState(
    BaseState,
    ContractStateMixing,
    ESCOContractStateMixing,
    CFASelectionContractStateMixing,
    CancellationBlockMixing,
    LimitedContractStateMixing,
    IgnoredClaimMixing,
):
    terminated_statuses = ("terminated", "cancelled")

    def always(self, data) -> None:
        self.set_mode_test(data)
        super().always(data)

    def set_mode_test(self, contract):
        if contract.get("mode") == "test":
            set_mode_test_titles(contract)

    def validate_patch_contract_items(self, request, before: dict, after: dict) -> None:
        # TODO: Remove this logic later with adding new endpoint for items in contract

        after_status = after.get("status", "active")
        if after_status == "active":
            self.validate_patch_active_contract_items(request, before, after)
        else:
            self.validate_patch_pending_contract_items(request, before, after)

    def validate_patch_pending_contract_items(self, request, before: dict, after: dict) -> None:
        item_patch_fields = [
            "unit",
            "quantity",
        ]
        items_before = before.get("items", [])
        items_after = after.get("items", [])
        for item_before, item_after in zip_longest(items_before, items_after):
            if None in (item_before, item_after):
                raise_operation_error(get_request(), "Can't change items list length")
            else:
                # check deletion of fields
                keys_difference = set(item_before.keys()) - set(item_after.keys())
                if keys_difference:
                    raise_operation_error(
                        get_request(),
                        f"Forbidden to delete fields {keys_difference}",
                    )
                for k in item_before.keys() | item_after.keys():
                    before, after = item_before.get(k), item_after.get(k)
                    if k not in item_patch_fields and before != after:
                        raise_operation_error(
                            get_request(),
                            f"Updated could be only {tuple(item_patch_fields)} in item, {k} change forbidden",
                        )
                    # check fields deletion in dict objects such as deliveryAddress, deliveryLocation, etc.
                    if isinstance(before, dict) and isinstance(after, dict) and set(before.keys()) - set(after.keys()):
                        raise_operation_error(
                            get_request(),
                            f"Forbidden to delete fields in {k}: {set(before.keys()) - set(after.keys())}",
                        )

                    if (
                        k == "unit"
                        and before is not None  # for ESCO there could be no unit for contract, but it can be added
                        and before.get("value")
                    ):
                        if before["value"]["currency"] != after["value"]["currency"]:
                            raise_operation_error(
                                get_request(),
                                "Forbidden to change currency in contract items unit",
                            )

    def extract_key_hash(self, item):
        """Make hash from field set"""
        key_tuple = (
            json.dumps(item.get("classification", {}), sort_keys=True, ensure_ascii=False),
            item.get("relatedLot", ""),
            item.get("relatedBuyer", ""),
            sorted(item.get("additionalClassifications", []), key=lambda a: a.get("id", "")),
        )
        return hashlib.sha1(
            json.dumps(key_tuple, sort_keys=True, ensure_ascii=False, default=str).encode(),
            usedforsecurity=False,
        ).hexdigest()

    def validate_patch_active_contract_items(self, request, before: dict, after: dict) -> None:
        old_items_keys = {self.extract_key_hash(item) for item in before.get("items", [])}
        new_items_keys = {self.extract_key_hash(item) for item in after.get("items", [])}

        error_msg = (
            "all main fields should be the same as in previous items: "
            "classification, relatedLot, relatedBuyer, additionalClassifications"
        )
        extra_keys = new_items_keys - old_items_keys
        if extra_keys:
            raise_operation_error(
                get_request(),
                f"Forbidden to add new items main information in contract, {error_msg}",
            )

        removed_keys = old_items_keys - new_items_keys
        if removed_keys:
            raise_operation_error(
                get_request(),
                f"Forbidden to delete items main information in contract, {error_msg}",
            )

    def validate_update_contracting_items_unit_value_amount(self, request, before, after) -> None:
        if after.get("items"):
            self._validate_contract_items_unit_value_amount(after)

    def _validate_contract_items_unit_value_amount(self, contract: dict) -> None:
        items_unit_value_amount = []
        for item in contract.get("items", ""):
            if item.get("unit") and item.get("quantity") is not None:
                if item["unit"].get("value"):
                    if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                        raise_operation_error(
                            get_request(),
                            "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0",
                            status=422,
                        )
                    items_unit_value_amount.append(
                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                    )

        validate_items_unit_amount(items_unit_value_amount, contract)

    @staticmethod
    def validate_update_contracting_value_identical(request, before, after):
        value = after.get("value")
        paid_data = request.validated["json_data"].get("amountPaid")
        for attr in ("currency",):
            if value and paid_data and paid_data.get(attr) is not None:
                if value.get(attr) != paid_data.get(attr):
                    raise_operation_error(
                        request,
                        f"{attr} of amountPaid should be identical to {attr} of value of contract",
                        name="amountPaid",
                    )

    @staticmethod
    def validate_update_contract_value_net_required(request, before, after, name="value"):
        value = after.get(name)
        if value and (before.get(name) != after.get(name) or before.get("status") != after.get("status", "active")):
            contract_amount_net = value.get("amountNet")
            if contract_amount_net is None:
                raise_operation_error(
                    request,
                    {"amountNet": BaseType.MESSAGES["required"]},
                    status=422,
                    name=name,
                )

    def validate_update_contract_paid_amount(self, request, before, after):
        value = after.get("value")
        paid = after.get("amountPaid")
        if not paid:
            return
        self.validate_update_contract_value_amount(request, before, after, name="amountPaid")
        if not value:
            return
        attr = "amountNet"
        paid_amount = paid.get(attr)
        value_amount = value.get(attr)
        if value_amount and paid_amount > value_amount:
            raise_operation_error(
                request,
                f"AmountPaid {attr} can`t be greater than value {attr}",
                name="amountPaid",
            )

    def validate_milestones(self, request, before, after):
        milestones_before = before.get("milestones", [])
        milestones_after = after.get("milestones", [])

        if milestones_before == milestones_after:
            return

        for milestone in milestones_after:
            validate_milestone_duration_days(get_tender(), milestone)

        if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM):
            validate_milestones_sequence_number(milestones_after)

        validate_milestone_sums(milestones_after)

    @staticmethod
    def validate_terminate_contract_without_amountPaid(request, before, after):
        if after.get("status", "active") == "terminated" and not after.get("amountPaid"):
            raise_operation_error(request, "Can't terminate contract while 'amountPaid' is not set")

    def on_patch(self, before, after) -> None:
        after["id"] = after["_id"]
        self.validate_contract_patch(self.request, before, after)
        if after.get("value"):
            self.synchronize_items_unit_value(after)
        super().on_patch(before, after)
        contract_changed = False
        if before["status"] == "pending":
            contract_changed = self.synchronize_contracts_data(after)
        self.contract_on_patch(before, after)

        self.request.validated["contract_was_changed"] = contract_changed

    @property
    def block_complaint_status(self):
        tender_type = get_tender().get("procurementMethodType", "")
        complaint_status = ("pending", "accepted", "satisfied")

        if tender_type == "closeFrameworkAgreementSelectionUA":
            complaint_status = ("answered", "pending")
        elif tender_type in (BELOW_THRESHOLD, REQUEST_FOR_PROPOSAL):
            complaint_status = ()

        return complaint_status

    def status_up(self, before: str, after: str, data: dict) -> None:
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_signed_info(data)
            self.validate_required_fields_before_activation(data)

    def validate_contract_patch(self, request, before: dict, after: dict) -> None:
        tender = get_tender()

        self.validate_dateSigned(request, tender, before, after)
        self.validate_update_contract_status(request, tender, before, after)
        self.validate_patch_contract_items(request, before, after)
        self.validate_milestones(request, before, after)
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)

        if after["status"] != "cancelled":
            if before["status"] == "pending":
                self.validate_contract_pending_patch(request, before, after)
            if after["status"] != "pending":
                self.validate_contract_active_patch(request, before, after)

    def check_agreements(self, tender: dict) -> bool:
        if tender["procurementMethodType"] == "closeFrameworkAgreementSelectionUA":
            return self.check_cfaseslectionua_agreements(tender)
        else:
            return super().check_agreements(tender)

    def check_award_complaints(self, tender: dict, now: datetime) -> None:
        if tender["procurementMethodType"] == "closeFrameworkAgreementSelectionUA":
            self.check_cfaseslectionua_award_complaints(tender, now)
        else:
            super().check_award_complaints(tender, now)

    def check_award_lot_complaints(self, tender: dict, lot_id: str, lot_awards: list, now: datetime) -> bool:
        if tender["procurementMethodType"] == "closeFrameworkAgreementSelectionUA":
            return self.check_cfaseslectionua_award_lot_complaints(tender, lot_id, lot_awards, now)
        else:
            return super().check_award_lot_complaints(tender, lot_id, lot_awards, now)

    def check_tender_status_method(self) -> None:
        tender_status_methods = {
            "belowThreshold": self.check_belowtreshold_status_method,
            "reporting": self.check_reporting_tender_status_method,
            "negotiation": self.check_negotiation_tender_status_method,
            "negotiation.quick": self.check_negotiation_tender_status_method,
            REQUEST_FOR_PROPOSAL: self.check_belowtreshold_status_method,
        }
        tender_type = self.request.validated["tender"]["procurementMethodType"]
        tender_status_method = tender_status_methods.get(tender_type, super().check_tender_status_method)
        tender_status_method()

    def check_belowtreshold_status_method(self) -> None:
        super().check_tender_status_method()
        self.check_ignored_claim(get_tender())

    def validate_contract_pending_patch(self, request, before: dict, after: dict) -> None:
        tender = get_tender()
        tender_type = tender.get("procurementMethodType", "")
        self.validate_contract_signing(before, after)
        self.add_esco_contract_duration_to_period(before, after)
        if tender_type in ("negotiation", "negotiation.quick"):
            self.validate_limited_contract_with_cancellations(before, after)

        award = request.validated["award"]
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))
        self.validate_update_contract_value_with_award(request, tender, before, after)

    def validate_contract_active_patch(self, request, before: dict, after: dict) -> None:
        self.validate_update_contracting_value_identical(request, before, after)
        self.validate_update_contracting_items_unit_value_amount(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after, name="amountPaid")
        self.validate_update_contract_paid_amount(request, before, after)
        self.validate_terminate_contract_without_amountPaid(request, before, after)
        self.validate_period(before, after)

    @staticmethod
    def validate_update_contract_value_with_award(request, tender: dict, before: dict, after: dict) -> None:
        if is_multi_currency_tender():
            return
        value = after.get("value")
        if value and (before.get("value") != after.get("value") or before.get("status") != after.get("status")):
            award = request.validated["award"]
            contracts_ids = [
                i["id"]
                for i in tender.get("contracts", [])
                if i.get("status", "") != "cancelled" and i["awardID"] == after["awardID"] and i["id"] != after["id"]
            ]

            _contracts_values = []

            if contracts_ids:
                _contracts_values = request.registry.mongodb.contracts.list(
                    fields={"value"},
                    filters={"_id": {"$in": contracts_ids}},
                    mode="_all_",
                )

            _contracts_values.append({"value": value})

            amount = sum(to_decimal(obj["value"].get("amount", 0)) for obj in _contracts_values)
            amount_net = sum(to_decimal(obj["value"].get("amountNet", 0)) for obj in _contracts_values)
            tax_included = value.get("valueAddedTaxIncluded")
            if tax_included:
                if award.get("value", {}).get("valueAddedTaxIncluded"):
                    if amount > to_decimal(award.get("value", {}).get("amount")):
                        raise_operation_error(
                            request,
                            "Amount should be less or equal to awarded amount",
                            name="value",
                        )
                else:
                    if amount_net > to_decimal(award.get("value", {}).get("amount")):
                        raise_operation_error(
                            request,
                            "AmountNet should be less or equal to awarded amount",
                            name="value",
                        )
            else:
                if amount > to_decimal(award.get("value", {}).get("amount")):
                    raise_operation_error(
                        request,
                        "Amount should be less or equal to awarded amount",
                        name="value",
                    )

    def validate_required_signed_info(self, data: dict) -> None:
        if "contractTemplateName" in data:
            buyer_signer_info = data.get("buyer", {}).get("signerInfo")
            supplier_signer_info = all(i.get("signerInfo") for i in data.get("suppliers", ""))
            if not buyer_signer_info or not supplier_signer_info:
                raise_operation_error(
                    self.request,
                    f"signerInfo field for buyer and suppliers "
                    f"is required for contract in `{data.get('status')}` status",
                    status=422,
                )

    def validate_required_fields_before_activation(self, data: dict) -> None:
        if not data.get("period", {}).get("startDate") or not data.get("period", {}).get("endDate"):
            raise_operation_error(
                self.request,
                "period is required for contract in `active` status",
                status=422,
            )
        if not data.get("contractNumber"):
            raise_operation_error(
                self.request,
                "contractNumber is required for contract in `active` status",
                status=422,
            )

    def validate_period(self, before, after):
        if before.get("period", {}).get("startDate") and not after.get("period", {}).get("startDate"):
            after["period"]["startDate"] = before["period"]["startDate"]
        if before.get("period", {}).get("endDate") and not after.get("period", {}).get("endDate"):
            after["period"]["endDate"] = before["period"]["endDate"]
        if (after.get("period", {}).get("startDate") and after.get("period", {}).get("endDate")) and dt_from_iso(
            after["period"]["endDate"]
        ) < dt_from_iso(after["period"]["startDate"]):
            raise_operation_error(
                self.request,
                "period should begin before its end",
                status=422,
            )

    def validate_dateSigned(self, request, tender, before: dict, after: dict) -> None:
        if before.get("dateSigned", "") == after.get("dateSigned", ""):
            return

        award = request.validated["award"]
        date_signed = dt_from_iso(after["dateSigned"])

        if award.get("complaintPeriod"):
            if not self.check_skip_award_complaint_period():
                if award.get("complaintPeriod", {}).get("endDate") and date_signed <= dt_from_iso(
                    award["complaintPeriod"]["endDate"]
                ):
                    raise_operation_error(
                        self.request,
                        [
                            f"Contract signature date should be after award complaint period end date ({award['complaintPeriod']['endDate']})"
                        ],
                        name="dateSigned",
                        status=422,
                    )
            elif award.get("complaintPeriod", {}).get("startDate") and date_signed <= dt_from_iso(
                award["complaintPeriod"]["startDate"]
            ):
                raise_operation_error(
                    self.request,
                    [
                        f"Contract signature date should be after award activation date ({award['complaintPeriod']['startDate']})"
                    ],
                    name="dateSigned",
                    status=422,
                )
        if date_signed > get_now():
            raise_operation_error(
                self.request,
                ["Contract signature date can't be in the future"],
                name="dateSigned",
                status=422,
            )

        if tender.get("procurementMethodType") == "priceQuotation" and date_signed < dt_from_iso(award.get("date")):
            raise_operation_error(
                self.request,
                [f"Contract signature date should be after award activation date ({award['date']})"],
                name="dateSigned",
                status=422,
            )

    @classmethod
    def validate_update_contract_status(cls, request, tender: dict, before: dict, after: dict) -> None:
        status_map = {
            "pending": ("pending.winner-signing", "active"),
            "pending.winner-signing": ("pending", "active"),
            "active": ("terminated",),
        }
        current_status = before["status"]
        new_status = after["status"]

        # Allow change contract status to cancelled for multi buyers tenders
        multi_contracts = len(tender.get("buyers", [])) > 1
        if multi_contracts:
            status_map["pending"] += ("cancelled",)
            status_map["pending.winner-signing"] += ("cancelled",)

        allowed_statuses_to = status_map.get(before["status"], [])

        # Validate status change
        if current_status != new_status and new_status not in allowed_statuses_to:
            raise_operation_error(request, "Can't update contract status")

        not_cancelled_contracts_count = sum(
            1
            for contract in tender.get("contracts", [])
            if (
                contract.get("status") != "cancelled"
                and contract.get("awardID") == request.validated["contract"]["awardID"]
            )
        )
        if multi_contracts and new_status == "cancelled" and not_cancelled_contracts_count == 1:
            raise_operation_error(
                request,
                f"Can't update contract status from {current_status} to {new_status} "
                f"for last not cancelled contract. Cancel award instead.",
            )

    def synchronize_contracts_data(self, data: dict) -> bool:
        fields_for_sync = ("status", "value")
        tender = get_tender()
        contracts = get_items(self.request, tender, "contracts", data["_id"], raise_404=False)
        if not contracts:
            LOGGER.error(
                f"Contract {data['_id']} not found in tender {tender['_id']}",
                context_unpack(self.request, {"MESSAGE_ID": "synchronize_contracts"}),
            )
            return False

        contract = contracts[0]
        contract_changed = False
        for field in fields_for_sync:
            old_value = contract.get(field)
            new_value = data.get(field)
            if (not old_value and new_value) or (old_value != new_value):
                if field == "status":
                    self.set_object_status(contract, data[field])
                else:
                    contract[field] = data[field]
                contract_changed = True

        return contract_changed

    def check_skip_award_complaint_period(self) -> bool:
        tender = get_tender()
        return tender.get("config", {}).get("hasAwardComplaints") is False

    def add_esco_contract_duration_to_period(self, before, after):
        request = get_request()
        tender = get_tender()
        if tender["procurementMethodType"] != "esco":
            return

        if not (period := after.get("period")) or before.get("period") == period:
            return

        award = request.validated["award"]
        bid = next((bid for bid in tender["bids"] if bid["id"] == award["bid_id"]), None)
        if not bid:
            return

        if award.get("lotID"):
            values = [
                lot_value["value"]
                for lot_value in bid.get("lotValues")
                if lot_value.get("relatedLot") == award["lotID"] and lot_value["status"] == "active"
            ]
            value = values[0] if values else {}
        else:
            value = bid.get("value", {})

        if not (duration := value.get("contractDuration")):
            return

        delta = timedelta(days=duration.get("years", 0) * 365 + duration.get("days", 0))
        if start_date := period.get("startDate"):
            end_date = calculate_full_date(parse_date(start_date), delta, ceil=True)
            period["endDate"] = end_date.isoformat()

    def set_author_of_object(self, data):
        contract = self.request.validated["contract"]
        if is_bid_owner(self.request, contract):
            data["author"] = "supplier"
        elif is_contract_owner(self.request, contract):
            data["author"] = "buyer"
        else:
            raise_operation_error(
                self.request,
                "Role isn't found, check auth and token",
            )
