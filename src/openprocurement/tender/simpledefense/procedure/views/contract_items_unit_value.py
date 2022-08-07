from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.openua.procedure.state.contract import OpenUAContractState
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="simple.defense",
    description="Tender contract items unit value",
)
class SimpleDefenseContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = OpenUAContractState
