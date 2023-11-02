from logging import getLogger

from openprocurement.contracting.core.procedure.state.contract import BaseContractState
from openprocurement.api.utils import raise_operation_error, context_unpack, get_now
from openprocurement.tender.core.procedure.utils import get_items, save_tender, dt_from_iso
from openprocurement.tender.pricequotation.procedure.state.contract import PQContractState
from openprocurement.api.constants import ECONTRACT_SIGNER_INFO_REQUIRED

LOGGER = getLogger(__name__)


TENDER_CONTRACT_STATE_MAP = {
    "priceQuotation": PQContractState
}


class EContractState(BaseContractState):
    terminated_statuses = ("terminated", "cancelled")

    def always(self, data) -> None:
        super().always(data)

    def on_patch(self, before, after) -> None:
        after["id"] = after["_id"]
        self.validate_contract_patch(self.request, before, after)
        super().on_patch(before, after)
        self.contract_on_patch(before, after)

        if before["status"] != after["status"]:
            if save_tender(self.request):
                LOGGER.info(
                    f"Updated tender {self.request.validated['tender']['_id']} contract {after['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_update_status"}),
                )

    def validate_contract_patch(self, request, before: dict, after: dict):
        # TODO: should be extended for other procedures, look to procedures contract states
        tender = request.validated["tender"]
        self.validate_dateSigned(request, tender, before, after)
        self.validate_update_contract_status(request, tender, before, after)
        self.validate_patch_contract_items(request, before, after)
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)

        if after["status"] == "pending":
            self.validate_contract_pending_patch(request, before, after)
        else:
            self.validate_contract_active_patch(request, before, after)

    def validate_contract_pending_patch(self, request, before, after):
        tender = request.validated["tender"]
        self.validate_contract_update_with_accepted_complaint(request, tender, before)
        self.validate_update_contract_value_with_award(request, before, after)
        # self.validate_update_contract_only_for_active_lots(request, tender, before)

    def validate_contract_active_patch(self, request, before, after):
        self.validate_update_contracting_value_identical(request, before, after)
        self.validate_update_contracting_items_unit_value_amount(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after, name="amountPaid")
        self.validate_update_contract_paid_amount(request, before, after)
        self.validate_terminate_contract_without_amountPaid(request, before, after)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_signed_info(data)
        if before != after and after in ["active", "cancelled"]:
            self.synchronize_contracts_data(data)

    def validate_required_signed_info(self, data):
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

    def validate_dateSigned(self, request, tender, before, after):
        if before.get("dateSigned", "") != after.get("dateSigned", ""):

            date_signed = dt_from_iso(after["dateSigned"])
            if date_signed > get_now():
                raise_operation_error(
                    self.request,
                    ["Contract signature date can't be in the future"],
                    name="dateSigned",
                    status=422,
                )
            active_award = [award for award in tender.get("awards", []) if award.get("status") == "active"]
            if active_award and date_signed < dt_from_iso(active_award[0].get("date")):
                raise_operation_error(
                    self.request,
                    [
                        f"Contract signature date should be "
                        f"after award activation date ({active_award[0]['date']})"
                    ],
                    name="dateSigned",
                    status=422,
                )

    @classmethod
    def validate_update_contract_status(cls, request, tender, before, after):

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

    def synchronize_contracts_data(self, data):
        tender = self.request.validated["tender"]
        contracts = get_items(self.request, tender, "contracts", data["_id"], raise_404=False)
        if not contracts:
            LOGGER.error(
                f"Contract {data['_id']} not found in tender {tender['_id']}",
                context_unpack(self.request, {"MESSAGE_ID": "synchronize_contracts"}),
            )
            return

        contract = contracts[0]
        self.set_object_status(contract, data["status"])
