from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.question import CFAUATenderQuestionState
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource

@resource(
    name="closeFrameworkAgreementUA:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender questions",
)
class CFAUATenderQuestionResource(TenderQuestionResource):
    state_class = CFAUATenderQuestionState
