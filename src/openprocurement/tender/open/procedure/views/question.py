from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.question import OpenTenderQuestionState


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender questions",
)
class UATenderQuestionResource(TenderQuestionResource):
    state_class = OpenTenderQuestionState
