from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.limited.procedure.state.criterion import LimitedCriterionState


@resource(
    name=f"{REPORTING}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender criteria",
)
class ReportingCriterionResource(BaseCriterionResource):
    state_class = LimitedCriterionState


@resource(
    name=f"{NEGOTIATION}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender criteria",
)
class NegotiationCriterionResource(ReportingCriterionResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender criteria",
)
class NegotiationQuickCriterionResource(ReportingCriterionResource):
    pass
