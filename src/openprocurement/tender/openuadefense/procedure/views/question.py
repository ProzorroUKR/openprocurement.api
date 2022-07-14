from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.openuadefense.procedure.state.question import DefenseTenderQuestionState


@resource(
    name="aboveThresholdUA.defense:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender questions",
)
class EUTenderQuestionResource(TenderQuestionResource):
    state_class = DefenseTenderQuestionState
