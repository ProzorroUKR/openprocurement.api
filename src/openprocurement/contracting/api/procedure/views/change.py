from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.change import (
    ContractsChangesResource,
)


@resource(
    name="Contract changes",
    collection_path="/contracts/{contract_id}/changes",
    path="/contracts/{contract_id}/changes/{change_id}",
    contractType="general",
    description="Contracts Changes",
)
class GeneralContractsChangesResource(ContractsChangesResource):
    """Contract changes resource"""

    pass
