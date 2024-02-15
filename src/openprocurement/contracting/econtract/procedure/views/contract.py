from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.api.context import get_request
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_update_not_in_allowed_status,
    validate_contract_owner,
)
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_input_data,
    unless_administrator,
    unless_admins,
)
from openprocurement.contracting.econtract.procedure.models.contract import (
    AdministratorPatchContract,
    PatchContract,
    PatchContractPending,
    Contract,
)
from openprocurement.contracting.econtract.procedure.state.contract import EContractState
from openprocurement.contracting.core.procedure.views.contract import ContractResource
from openprocurement.contracting.core.procedure.serializers.contract import ContractBaseSerializer


def conditional_contract_model(data):
    request = get_request()
    contract_status = request.validated["contract"]["status"]
    if request.authenticated_role == "Administrator":
        model = AdministratorPatchContract
    elif contract_status == "pending":
        model = PatchContractPending
    else:
        model = PatchContract
    return model(data)


@resource(
    name="EContract",
    path="/contracts/{contract_id}",
    description="Econtracts operations",
    contractType="econtract",
    accept="application/json",
)
class EContractResource(ContractResource):
    state_class = EContractState
    serializer_class = ContractBaseSerializer

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_owner)),
            validate_input_data(conditional_contract_model),
            validate_patch_data_simple(Contract, item_name="contract"),
            unless_admins(unless_administrator(validate_contract_update_not_in_allowed_status)),
        ),
    )
    def patch(self):
        return super().patch()
