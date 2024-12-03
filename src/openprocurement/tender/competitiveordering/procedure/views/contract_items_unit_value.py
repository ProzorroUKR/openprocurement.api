from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.contract import (
    OpenContractState,
)
from openprocurement.tender.core.procedure.views.contract_items_unit_value import (
    ContractItemsUnitValueResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender contract items unit value",
)
class UAContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = OpenContractState
