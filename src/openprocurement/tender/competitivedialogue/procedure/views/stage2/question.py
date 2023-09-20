from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE,
    STAGE_2_EU_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.question import (
    CDEUStage2TenderQuestionState,
    CDUAStage2TenderQuestionState,
)
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender questions",
)
class CDEUTenderQuestionResource(TenderQuestionResource):
    state_class = CDEUStage2TenderQuestionState


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender questions",
)
class CDUATenderQuestionResource(TenderQuestionResource):
    state_class = CDUAStage2TenderQuestionState
