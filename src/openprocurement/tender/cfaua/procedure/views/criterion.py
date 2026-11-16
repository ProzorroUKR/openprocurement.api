from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaua.procedure.state.criterion import CFAUACriterionState
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name="closeFrameworkAgreementUA:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = CFAUACriterionState
