from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_change_action_not_in_allowed_contract_status,
    validate_contract_participant,
    validate_create_contract_change,
)
from openprocurement.contracting.core.procedure.views.change import (
    ContractsChangesResource as BaseContractsChangesResource,
)
from openprocurement.contracting.econtract.procedure.models.change import PostChange
from openprocurement.contracting.econtract.procedure.state.change import EChangeState


@resource(
    name="EContract changes",
    collection_path="/contracts/{contract_id}/changes",
    path="/contracts/{contract_id}/changes/{change_id}",
    contractType="eContract",
    description="EContracts Changes",
)
class EContractsChangesResource(BaseContractsChangesResource):
    state_class = EChangeState

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_administrator(unless_admins(validate_contract_participant)),
            validate_input_data(PostChange),
            validate_contract_change_action_not_in_allowed_contract_status,
            validate_create_contract_change,
        ),
    )
    def collection_post(self):
        return super().collection_post()
