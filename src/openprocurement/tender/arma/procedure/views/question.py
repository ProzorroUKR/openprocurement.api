from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.question import QuestionState
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource


@resource(
    name="complexAsset.arma:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender questions",
)
class QuestionResource(TenderQuestionResource):
    state_class = QuestionState
