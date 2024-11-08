from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract_items_unit_value import (
    ContractItemsUnitValueResource,
)
from openprocurement.tender.requestforproposal.procedure.state.contract import (
    RequestForProposalContractState,
)


@resource(
    name="requestForProposal:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="requestForProposal",
    description="Tender contract items unit value",
)
class BTContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = RequestForProposalContractState
