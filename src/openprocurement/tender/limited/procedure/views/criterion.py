from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.limited.procedure.state.criterion import (
    NegotiationCriterionState,
    NegotiationQuickCriterionState,
    ReportingCriterionState,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{ProcurementMethodType.REPORTING}",
    description="Tender criteria",
)
class ReportingCriterionResource(BaseCriterionResource):
    state_class = ReportingCriterionState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION}",
    description="Tender criteria",
)
class NegotiationCriterionResource(ReportingCriterionResource):
    state_class = NegotiationCriterionState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION_QUICK}",
    description="Tender criteria",
)
class NegotiationQuickCriterionResource(ReportingCriterionResource):
    state_class = NegotiationQuickCriterionState
