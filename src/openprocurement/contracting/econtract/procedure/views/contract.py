from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.context import get_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_update_contract_value_net_required,
    validate_update_contract_paid_net_required,
    validate_update_contracting_value_readonly,
    validate_update_contracting_value_identical,
    validate_update_contracting_value_amount,
    validate_update_contracting_paid_amount,
    validate_contract_update_not_in_allowed_status,
    validate_terminate_contract_without_amountPaid,
    validate_contract_participant,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    unless_administrator,
)
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.contracting.econtract.procedure.models.contract import (
    AdministratorPatchContract,
    PatchContract,
    PatchSupplierContract,
    Contract,
)
from openprocurement.contracting.econtract.procedure.state.contract import EContractState
from openprocurement.contracting.core.procedure.views.contract import ContractResource
from openprocurement.contracting.core.procedure.serializers.contract import ContractBaseSerializer
from openprocurement.contracting.core.procedure.utils import is_contract_owner, is_bid_owner


def conditional_contract_model(data):
    contract = get_contract()
    request = get_request()
    if request.authenticated_role == "Administrator":
        model = AdministratorPatchContract
    elif is_bid_owner(request, contract):
        model = PatchSupplierContract
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
            unless_admins(unless_administrator(validate_contract_participant)),
            validate_input_data(conditional_contract_model, none_means_remove=True),
            validate_patch_data_simple(Contract, item_name="contract"),
            unless_admins(unless_administrator(validate_contract_update_not_in_allowed_status)),
            validate_update_contract_value_net_required,
            validate_update_contract_paid_net_required,
            validate_update_contracting_value_readonly,
            validate_update_contracting_value_identical,
            validate_update_contracting_value_amount,
            validate_update_contracting_paid_amount,
            validate_terminate_contract_without_amountPaid,
        ),
    )
    def patch(self):
        return super().patch()
