from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.esco.procedure.state.contract import ESCOContractState
from cornice.resource import resource


@resource(
    name="esco:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="esco",
    description="Tender contract items unit value",
)
class ESCOContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = ESCOContractState
