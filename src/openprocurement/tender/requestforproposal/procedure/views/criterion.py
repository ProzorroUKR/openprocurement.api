from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.requestforproposal.procedure.state.criterion import (
    RequestForProposalCriterionState,
)


@resource(
    name="requestForProposal:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="requestForProposal",
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = RequestForProposalCriterionState
