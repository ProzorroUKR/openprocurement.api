from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.api.utils import context_unpack, error_handler, json_view
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_active_status,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.econtract.procedure.models.contract import Contract
from openprocurement.contracting.econtract.procedure.models.termination_details import (
    PatchContractTerminationDetails,
)
from openprocurement.contracting.econtract.procedure.serializers.termination_details import (
    ContractContextSerializer,
    TerminationDetailsSerializer,
)
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)
from openprocurement.contracting.econtract.procedure.validation import (
    prepare_termination_details_patch,
    validate_termination_details_buyer_only,
)
from openprocurement.tender.core.utils import context_view


def resolve_termination_details(request):
    contract = request.validated["contract"]
    termination_details = contract.get("terminationDetails")
    if not termination_details:
        request.errors.add("url", "termination_details", "Not Found")
        request.errors.status = 404
        raise error_handler(request)
    request.validated["termination_details"] = termination_details


@resource(
    name="EContract termination_details",
    path="/contracts/{contract_id}/termination_details",
    contractType="eContract",
    description="EContract terminationDetails",
    request_method=("GET", "PATCH"),
)
class EContractTerminationDetailsResource(ContractBaseResource):
    state_class = EContractState

    @json_view(permission="view_contract")
    @context_view(
        objs={
            "contract": (ContractContextSerializer, None),
        }
    )
    def get(self):
        resolve_termination_details(self.request)
        termination_details = self.request.validated["termination_details"]
        return {"data": TerminationDetailsSerializer(termination_details).data}

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_termination_details_buyer_only)),
            unless_admins(unless_administrator(validate_contract_in_active_status)),
            validate_input_data(PatchContractTerminationDetails),
            prepare_termination_details_patch,
            validate_patch_data_simple(Contract, item_name="contract"),
        ),
    )
    def patch(self):
        updated = self.request.validated["data"]
        contract_src = self.request.validated["contract_src"]
        if not updated:
            return
        contract = self.request.validated["contract"] = updated
        self.state.on_patch(contract_src, contract)
        if save_contract(self.request):
            self.LOGGER.info(
                f"Updated contract {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {
                "data": TerminationDetailsSerializer(contract.get("terminationDetails")).data,
                "config": contract["config"],
            }
