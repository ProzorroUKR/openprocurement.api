from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionState

@resource(
    name="aboveThresholdUA:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender questions",
)
class UATenderQuestionResource(TenderQuestionResource):
    state_class = UATenderQuestionState
