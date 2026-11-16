from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.question import (
    CDStage1EUTenderQuestionState,
    CDStage1UATenderQuestionState,
)
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender questions",
)
class Stage1EUTenderQuestionResource(TenderQuestionResource):
    state_class = CDStage1EUTenderQuestionState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender questions",
)
class Stage1UATenderQuestionResource(TenderQuestionResource):
    state_class = CDStage1UATenderQuestionState
