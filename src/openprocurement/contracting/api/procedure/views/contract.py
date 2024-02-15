from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.api.context import get_request
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_owner,
    validate_contract_update_not_in_allowed_status,
)
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_input_data,
    unless_administrator,
    unless_admins,
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
            unless_admins(unless_administrator(validate_contract_owner)),
            validate_input_data(conditional_contract_model),
            validate_patch_data_simple(Contract, item_name="contract"),
            unless_admins(unless_administrator(validate_contract_update_not_in_allowed_status)),
        ),
    )
    def patch(self):
        return super().patch()
