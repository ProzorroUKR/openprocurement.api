from datetime import datetime, timedelta
from decimal import Decimal
from itertools import zip_longest
from logging import getLogger
from typing import Callable

from pyramid.request import Request

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_request, get_tender
from openprocurement.api.procedure.utils import get_items, parse_date, to_decimal
from openprocurement.api.utils import (
    calculate_full_date,
    context_unpack,
    get_first_revision_date,
    get_now,
    raise_operation_error,
)
from openprocurement.contracting.core.procedure.state.contract import BaseContractState
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    IgnoredClaimMixing,
)
from openprocurement.tender.core.procedure.cancelling import CancellationBlockMixing
from openprocurement.tender.core.procedure.utils import (
    contracts_allow_to_complete,
    dt_from_iso,
    is_multi_currency_tender,
)
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL

LOGGER = getLogger(__name__)


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

    def validate_contract_with_cancellations_and_contract_signing(self, before: dict, after: dict) -> None:
        tender = get_tender()
        new_rules = get_first_revision_date(tender, default=get_request_now()) > RELEASE_2020_04_19

        if before.get("status") != "active" and after.get("status") == "active":
            award_id = self.request.validated["contract"].get("awardID")
            award = [a for a in tender.get("awards") if a["id"] == award_id][0]
            lot_id = award.get("lotID")
            stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("endDate"))
            if stand_still_end > get_request_now():
                raise_operation_error(
                    self.request,
                    f"Can't sign contract before stand-still period end ({stand_still_end.isoformat()})",
                )

            blocked_complaints = any(
                c["status"] in self.block_complaint_status and a.get("lotID") == lot_id
                for a in tender["awards"]
                for c in award.get("complaints", "")
            )

            new_rules_block_complaints = any(
                complaint["status"] in self.block_complaint_status and cancellation.get("relatedLot") == lot_id
                for cancellation in tender.get("cancellations", "")
                for complaint in cancellation.get("complaints", "")
            )

            if blocked_complaints or (new_rules and new_rules_block_complaints):
                raise_operation_error(self.request, "Can't sign contract before reviewing all complaints")

    def check_reporting_tender_status_method(self) -> None:
        self.check_contracts_statuses(self.request.validated["tender"])

    def check_negotiation_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        if tender.get("lots"):
            self.check_contracts_lot_statuses(tender)
        else:
            self.check_contracts_statuses(tender)


class EContractState(
    BaseContractState,
    ESCOContractStateMixing,
    CFASelectionContractStateMixing,
    CancellationBlockMixing,
    LimitedContractStateMixing,
    IgnoredClaimMixing,
):
    terminated_statuses = ("terminated", "cancelled")

    def always(self, data) -> None:
        super().always(data)

    def on_patch(self, before, after) -> None:
        after["id"] = after["_id"]
        self.convert_items_attributes_types(before, after)
        self.validate_contract_patch(self.request, before, after)
        super().on_patch(before, after)
        contract_changed = False
        if before["status"] == "pending":
            contract_changed = self.synchronize_contracts_data(after)
        self.contract_on_patch(before, after)

        self.request.validated["contract_was_changed"] = contract_changed

    @property
    def block_complaint_status(self):
        tender_type = get_tender().get("procurementMethodType", "")
        complaint_status = ("pending", "accepted", "satisfied", "stopping")

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
        if tender_type in (
            "belowThreshold",
            "aboveThresholdEU",
            "aboveThresholdUA",
            "aboveThresholdUA.defense",
            "aboveThreshold",
            "simple.defense",
            "esco",
            "competitiveDialogueEU.stage2",
            "competitiveDialogueUA.stage2",
            REQUEST_FOR_PROPOSAL,
        ):
            self.validate_threshold_contract(request, before, after)
        elif tender_type in ("negotiation", "negotiation.quick"):
            self.validate_limited_negotiation_contract(request, before, after)

        award = request.validated["award"]
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))
        self.validate_update_contract_value_with_award(request, tender, before, after)

    def validate_threshold_contract(self, request, before: dict, after: dict) -> None:
        self.validate_contract_signing(before, after)
        self.add_esco_contract_duration_to_period(before, after)

    def validate_limited_negotiation_contract(self, request, before: dict, after: dict) -> None:
        self.validate_contract_with_cancellations_and_contract_signing(before, after)

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
                [f"Contract signature date should be " f"after award activation date ({award['date']})"],
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

    def convert_items_attributes_types(self, before: dict, after: dict):
        if "items" not in before:
            return

        items_before = before.get("items", [])
        items_after = after.get("items", [])
        for item_before, item_after in zip_longest(items_before, items_after):
            if not item_before or not item_after:
                continue

            attrs_before = item_before.get("attributes", [])
            attrs_after = item_after.get("attributes", [])

            for attr_before, attr_after in zip_longest(attrs_before, attrs_after):
                if not attr_before or not attr_after:
                    continue
                if "values" in attr_before:
                    value_type = type(attr_before["values"][0])
                else:
                    value_type = type(attr_before["value"])
                if value_type is Decimal:
                    value_type = to_decimal
                try:
                    if "values" in attr_after:
                        attr_after["values"] = [value_type(i) for i in attr_after["values"]]
                    elif "value" in attr_after:
                        attr_after["value"] = value_type(attr_after["value"])
                except TypeError:
                    raise_operation_error(self.request, "items attributes type mismatch.", status=422)

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
