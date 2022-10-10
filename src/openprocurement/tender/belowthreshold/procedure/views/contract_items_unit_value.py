from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.belowthreshold.procedure.state.contract import BelowThresholdContractState
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="belowThreshold",
    description="Tender contract items unit value",
)
class BTContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = BelowThresholdContractState
