from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.pricequotation.procedure.state.contract import PQContractState
from cornice.resource import resource


@resource(
    name="priceQuotation:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="priceQuotation",
    description="Tender contract items unit value",
)
class PQContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = PQContractState
