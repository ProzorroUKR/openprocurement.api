from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.views.change import (
    ContractsChangesResource as BaseContractsChangesResource,
)
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
    )
    def collection_post(self):
        return super().collection_post()
