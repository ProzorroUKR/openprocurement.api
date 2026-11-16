from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.question import (
    CDStage2EUTenderQuestionState,
    CDStage2UATenderQuestionState,
)
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Tender questions",
)
class CDEUTenderQuestionResource(TenderQuestionResource):
    state_class = CDStage2EUTenderQuestionState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Tender questions",
)
class CDUATenderQuestionResource(TenderQuestionResource):
    state_class = CDStage2UATenderQuestionState
