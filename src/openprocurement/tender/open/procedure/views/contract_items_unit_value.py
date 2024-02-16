from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract_items_unit_value import (
    ContractItemsUnitValueResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.contract import OpenContractState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender contract items unit value",
)
class UAContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = OpenContractState
