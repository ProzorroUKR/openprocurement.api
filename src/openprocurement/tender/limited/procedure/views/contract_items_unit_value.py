from openprocurement.tender.core.procedure.views.contract_items_unit_value import ContractItemsUnitValueResource
from openprocurement.tender.limited.procedure.state.contract import (
    LimitedReportingContractState,
    LimitedNegotiationContractState,
)
from cornice.resource import resource


@resource(
    name="reporting:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="reporting",
    description="Tender contract items unit value",
)
class ReportingContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = LimitedReportingContractState


@resource(
    name="negotiation:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="negotiation",
    description="Tender contract items unit value",
)
class NegotiationContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = LimitedNegotiationContractState


@resource(
    name="negotiation.quick:Tender Contract Items Unit Value",
    path="/tenders/{tender_id}/contracts/{contract_id}/items/{item_id}/unit/value",
    procurementMethodType="negotiation.quick",
    description="Tender contract items unit value",
)
class NQContractItemsUnitValueResource(ContractItemsUnitValueResource):
    state_class = LimitedNegotiationContractState
