from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.competitivedialogue.procedure.state.stage1.question import (
    Stage1TenderQuestionState,
)

@resource(
    name=f"{CD_EU_TYPE}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender questions",
)
class Stage1EUTenderQuestionResource(TenderQuestionResource):
    state_class = Stage1TenderQuestionState

@resource(
    name=f"{CD_UA_TYPE}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender questions",
)
class Stage1UATenderQuestionResource(TenderQuestionResource):
    state_class = Stage1TenderQuestionState
