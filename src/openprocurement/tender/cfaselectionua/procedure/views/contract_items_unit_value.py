from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.cfaselectionua.procedure.state.contract import CFASelectionContractState
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender contract items unit value",
)
class CFASelectionContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = CFASelectionContractState
