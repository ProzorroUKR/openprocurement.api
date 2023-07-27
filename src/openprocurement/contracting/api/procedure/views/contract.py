from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.api.context import get_request
from openprocurement.contracting.core.procedure.validation import (
    validate_update_contract_value_net_required,
    validate_update_contract_paid_net_required,
    validate_update_contracting_value_readonly,
    validate_update_contracting_value_identical,
    validate_update_contracting_value_amount,
    validate_update_contracting_paid_amount,
    validate_contract_update_not_in_allowed_status,
    validate_terminate_contract_without_amountPaid,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    unless_administrator,
    validate_item_owner,
)
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.contracting.api.procedure.models.contract import (
    PatchContract,
    AdministratorPatchContract,
    Contract,
)
from openprocurement.contracting.core.procedure.views.contract import ContractResource


def conditional_contract_model(data):
    if get_request().authenticated_role == "Administrator":
        model = AdministratorPatchContract
    else:
        model = PatchContract
    return model(data)


@resource(
    name="Contract",
    # collection_path="/contracts",
    path="/contracts/{contract_id}",
    description="Base operations for general contracts",
    contractType="general",
    accept="application/json",
)
class GeneralContractResource(ContractResource):

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("contract"))),
            validate_input_data(conditional_contract_model),
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
