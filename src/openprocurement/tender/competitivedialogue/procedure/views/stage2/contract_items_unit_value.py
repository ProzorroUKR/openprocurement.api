from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.openua.procedure.state.contract import OpenUAContractState
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender contract items unit value",
)
class EU2ContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = OpenUAContractState


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender contract items unit value",
)
class UA2ContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = OpenUAContractState
