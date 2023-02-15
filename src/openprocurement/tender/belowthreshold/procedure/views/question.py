from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.belowthreshold.procedure.state.question import BelowThresholdTenderQuestionState

@resource(
    name="belowThreshold:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="belowThreshold",
    description="Tender questions",
)
class BelowThresholdTenderQuestionResource(TenderQuestionResource):
    state_class = BelowThresholdTenderQuestionState
