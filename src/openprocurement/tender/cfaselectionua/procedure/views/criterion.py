from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.cfaselectionua.procedure.state.criterion import CFASelectionCriterionState


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = CFASelectionCriterionState
