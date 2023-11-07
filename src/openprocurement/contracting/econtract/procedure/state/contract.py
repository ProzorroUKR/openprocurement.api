from logging import getLogger
from datetime import datetime

from openprocurement.contracting.core.procedure.state.contract import BaseContractState
from openprocurement.api.utils import raise_operation_error, context_unpack, get_now, to_decimal
from openprocurement.tender.core.procedure.utils import (
    get_items,
    save_tender,
    dt_from_iso,
    get_contracts_values_related_to_patched_contract,
)
from openprocurement.tender.core.procedure.cancelling import CancellationBlockMixing
from openprocurement.tender.esco.procedure.state.contract import ESCOContractStateMixing
from openprocurement.tender.cfaselectionua.procedure.state.contract import CFASelectionContractStateMixing
from openprocurement.tender.limited.procedure.state.contract import LimitedContractStateMixing
from openprocurement.tender.belowthreshold.procedure.state.tender import IgnoredClaimMixing
from openprocurement.api.constants import ECONTRACT_SIGNER_INFO_REQUIRED

LOGGER = getLogger(__name__)


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
        self.validate_contract_patch(self.request, before, after)
        super().on_patch(before, after)
        contract_changed = False
        if before["status"] == "pending":
            contract_changed = self.synchronize_contracts_data(after)
        self.contract_on_patch(before, after)

        if contract_changed:
            if save_tender(self.request):
                LOGGER.info(
                    f"Updated tender {self.request.validated['tender']['_id']} contract {after['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_update_status"}),
                )

    @property
    def block_complaint_status(self):
        tender = self.request.validated["tender"]
        tender_type = tender["procurementMethodType"]
        complaint_status = ("pending", "accepted", "satisfied", "stopping")

        if tender_type == "closeFrameworkAgreementSelectionUA":
            complaint_status = ("answered", "pending")
        elif tender_type == "belowThreshold":
            complaint_status = ()

        return complaint_status

    def status_up(self, before: str, after: str, data: dict) -> None:
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_signed_info(data)

    def validate_contract_patch(self, request, before: dict, after: dict) -> None:
        tender = request.validated["tender"]

        self.validate_patch_esco_value_fields(request, tender, before, after)
        self.validate_dateSigned(request, tender, before, after)
        self.validate_update_contract_status(request, tender, before, after)
        self.validate_patch_contract_items(request, before, after)
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)

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
            "negotiation.quick": self.check_negotiation_tender_status_method
        }
        tender_type = self.request.validated["tender"]["procurementMethodType"]
        tender_status_method = tender_status_methods.get(tender_type, super().check_tender_status_method)
        tender_status_method()

    def check_belowtreshold_status_method(self) -> None:
        super().check_tender_status_method()
        tender = self.request.validated["tender"]
        self.check_ignored_claim(tender)

    def validate_contract_pending_patch(self, request, before: dict, after: dict) -> None:
        tender = request.validated["tender"]
        tender_type = tender["procurementMethodType"]
        if tender_type in ("belowThreshold", "aboveThresholdEU",
                           "aboveThresholdUA", "aboveThreshold", "simple.defense"):
            self.validate_threshold_contract(request, before, after)
        elif tender_type == "esco":
            self.validate_esco_contract(request, before, after)
        elif tender_type in ("negotiation", "negotiation.quick"):
            self.validate_limited_negotiation_contract(request, before, after)

        award = request.validated["award"]
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))
        self.validate_contract_update_with_accepted_complaint(request, tender, before)
        self.validate_update_contract_value_with_award(request, before, after)
        # self.validate_update_contract_only_for_active_lots(request, tender, before)

    def validate_threshold_contract(self, request, before: dict, after: dict) -> None:
        self.validate_contract_signing(before, after)

    def validate_esco_contract(self, request, before: dict, after: dict) -> None:
        self.validate_contract_signing(before, after)
        self.validate_update_contract_value_esco(request, before, after, False)

    def validate_limited_negotiation_contract(self, request, before: dict, after: dict) -> None:
        self.validate_contract_with_cancellations_and_contract_signing(before, after)

    def validate_contract_active_patch(self, request, before: dict, after: dict) -> None:
        self.validate_update_contracting_value_identical(request, before, after)
        self.validate_update_contracting_items_unit_value_amount(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after, name="amountPaid")
        self.validate_update_contract_paid_amount(request, before, after)
        self.validate_terminate_contract_without_amountPaid(request, before, after)

    @staticmethod
    def validate_patch_esco_value_fields(request, tender: dict, before: dict, after: dict) -> None:
        ESCO_FIELDS = {
            "amountPerformance",
            "yearlyPaymentsPercentage",
            "annualCostsReduction",
            "contractDuration",
        }

        if tender.get("procurementMethodType") == "esco" or not after.get("value"):
            return

        esco_fields_in_contract = ESCO_FIELDS & after["value"].keys()
        if esco_fields_in_contract:
            raise_operation_error(
                request,
                [{f: "Rogue field"for f in esco_fields_in_contract}],
                status=422,
                name="value",
            )

    @staticmethod
    def validate_update_contract_value_with_award(request, before: dict, after: dict) -> None:
        value = after.get("value")
        if value and (
                before.get("value") != after.get("value") or
                before.get("status") != after.get("status")
        ):

            award = request.validated["award"]
            _contracts_values = request.registry.mongodb.contracts.list(
                fields={"value"},
                filters={
                    "_id": {"$ne": after["id"]},
                    "tender_id": after["tender_id"],
                    "awardID": after["awardID"],
                    "status": {"$ne": "cancelled"}
                }
            )
            _contracts_values.append({"value": value})

            amount = sum([to_decimal(obj["value"].get("amount", 0)) for obj in _contracts_values])
            amount_net = sum([to_decimal(obj["value"].get("amountNet", 0)) for obj in _contracts_values])
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

    def validate_required_signed_info(self, data: dict) -> None:
        if not ECONTRACT_SIGNER_INFO_REQUIRED:
            return

        supplier_signer_info = all(i.get("signerInfo") for i in data.get("suppliers", ""))
        if not data.get("buyer", {}).get("signerInfo") or not supplier_signer_info:
            raise_operation_error(
                self.request,
                f"signerInfo field for buyer and suppliers "
                f"is required for contract in `{data.get('status')}` status",
                status=422
            )

    def validate_dateSigned(self, request, tender, before: dict, after: dict) -> None:
        if before.get("dateSigned", "") == after.get("dateSigned", ""):
            return

        award = request.validated["award"]
        date_signed = dt_from_iso(after["dateSigned"])

        if award.get("complaintPeriod"):
            if not self.check_skip_award_complaint_period():
                if (award.get("complaintPeriod", {}).get("endDate") and
                        date_signed <= dt_from_iso(award["complaintPeriod"]["endDate"])):
                    raise_operation_error(
                        self.request,
                        [f"Contract signature date should be after award complaint period end date ({award['complaintPeriod']['endDate']})"],
                        name="dateSigned",
                        status=422,
                    )
            elif (award.get("complaintPeriod", {}).get("startDate") and
                  date_signed <= dt_from_iso(award["complaintPeriod"]["startDate"])):
                raise_operation_error(
                    self.request,
                    [f"Contract signature date should be after award activation date ({award['complaintPeriod']['startDate']})"],
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

        if (
            tender.get("procurementMethodType") == "priceQuotation"
            and date_signed < dt_from_iso(award.get("date"))
        ):
            raise_operation_error(
                self.request,
                [
                    f"Contract signature date should be "
                    f"after award activation date ({award['date']})"
                ],
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
            status_map["pending"] += ("cancelled", )
            status_map["pending.winner-signing"] += ("cancelled",)

        allowed_statuses_to = status_map.get(before["status"], list())

        # Validate status change
        if (
            current_status != new_status
            and new_status not in allowed_statuses_to
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

    def synchronize_contracts_data(self, data: dict) -> bool:
        fields_for_sync = ("status", "value")
        tender = self.request.validated["tender"]
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
        tender = self.request.validated["tender"]
        return tender.get("procurementMethodType") == "belowThreshold"
