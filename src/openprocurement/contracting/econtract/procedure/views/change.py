from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.change import (
    ContractsChangesResource,
)


@resource(
    name="EContract changes",
    collection_path="/contracts/{contract_id}/changes",
    path="/contracts/{contract_id}/changes/{change_id}",
    description="EContracts Changes",
)
class EContractsChangesResource(ContractsChangesResource):
    pass
