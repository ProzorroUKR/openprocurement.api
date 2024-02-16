from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.contract import (
    CFASelectionContractState,
)
from openprocurement.tender.core.procedure.views.contract_items_unit_value import (
    ContractItemsUnitValueResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender contract items unit value",
)
class CFASelectionContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = CFASelectionContractState
