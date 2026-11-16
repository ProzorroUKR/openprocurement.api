from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.procedure.state.question import ARMAQuestionState
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource


@resource(
    name=f"{ProcurementMethodType.COMPLEX_ASSET_ARMA}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=ProcurementMethodType.COMPLEX_ASSET_ARMA,
    description="Tender questions",
)
class QuestionResource(TenderQuestionResource):
    state_class = ARMAQuestionState
