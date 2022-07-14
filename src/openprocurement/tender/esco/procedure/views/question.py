from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.esco.procedure.state.question import ESCOTenderQuestionState

@resource(
    name="esco:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="esco",
    description="Tender questions",
)
class ESCOTenderQuestionResource(TenderQuestionResource):
    state_class = ESCOTenderQuestionState
