from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.openeu.procedure.state.question import EUTenderQuestionState

@resource(
    name="aboveThresholdEU:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender questions",
)
class EUTenderQuestionResource(TenderQuestionResource):
    state_class = EUTenderQuestionState
