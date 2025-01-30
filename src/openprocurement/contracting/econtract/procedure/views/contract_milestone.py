from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.contract_milestone import (
    ContractMilestoneResource,
)


@resource(
    name="EContract milestones",
    collection_path="/contracts/{contract_id}/milestones",
    path="/contracts/{contract_id}/milestones/{milestone_id}",
    description="Econtracts milestones operations",
    accept="application/json",
)
class EContractMilestoneResource(ContractMilestoneResource):
    pass
