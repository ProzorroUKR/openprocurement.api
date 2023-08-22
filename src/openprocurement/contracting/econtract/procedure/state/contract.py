from logging import getLogger
from copy import deepcopy

from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.contracting.core.utils import get_tender_by_id
from openprocurement.api.utils import raise_operation_error, context_unpack
from openprocurement.tender.core.procedure.utils import get_items, save_tender
from openprocurement.tender.pricequotation.procedure.state.contract import PQContractState

LOGGER = getLogger(__name__)


TENDER_CONTRACT_STATE_MAP = {
    "priceQuotation": PQContractState
}


class EContractState(ContractState):
    terminated_statuses = ("terminated", "cancelled")

    def always(self, data) -> None:
        super().always(data)

    # def get_tender_state(self, contract):
    #     tender = get_tender_by_id(self.request, tender_id=contract["tender_id"])
    #     self.request.validated["tender"] = tender
    #     self.request.validated["tender_src"] = deepcopy(tender)
    #     awards = get_items(self.request, tender, "awards", contract["awardID"])
    #     self.request.validated["award"] = awards[0]
    #     return TENDER_CONTRACT_STATE_MAP.get(tender["procurementMethodType"])(self.request)

    def on_patch(self, before, after) -> None:
        tender = get_tender_by_id(self.request, tender_id=after["tender_id"])
        self.request.validated["tender"] = tender
        self.request.validated["tender_src"] = deepcopy(tender)
        after["id"] = after["_id"]
        # tender_state = self.get_tender_state(after)
        self.validate_contract_patch(self.request, before, after)
        super().on_patch(before, after)
        self.contract_on_patch(before, after)
        # tender_state.validate_contract_patch(self.request, before, after)
        # tender_state.contract_on_patch(before, after)

        if before["status"] != after["status"]:
            if save_tender(self.request):
                LOGGER.info(
                    f"Updated tender {self.request.validated['tender']['_id']} contract {after['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_update_status"}),
                )

    def validate_contract_patch(self, request, before: dict, after: dict):
        tender = request.validated["tender"]

        self.validate_contract_items(before, after)
        # self.validate_update_contract_only_for_active_lots(request, tender, before)
        # self.validate_update_contract_status_by_supplier(request, before, after)
        self.validate_update_contract_status(request, tender, before, after)
        self.validate_contract_update_with_accepted_complaint(request, tender, before)  # openua
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_with_award(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_signed_info(data)
        self.synchronize_contracts_data(data)

    def validate_required_signed_info(self, data):
        supplier_signer_info = all(i.get("signerInfo") for i in data.get("suppliers", ""))
        if not data.get("buyer", {}).get("signerInfo") or not supplier_signer_info:
            raise_operation_error(
                self.request,
                f"signerInfo field for buyer and suppliers "
                f"is required for contract in `{data.get('status')}` status",
                status=422
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
        contract["status"] = data["status"]
