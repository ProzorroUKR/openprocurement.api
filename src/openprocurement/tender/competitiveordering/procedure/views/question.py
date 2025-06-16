from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.question import (
    COTenderQuestionState,
)
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender questions",
)
class COTenderQuestionResource(TenderQuestionResource):
    state_class = COTenderQuestionState
