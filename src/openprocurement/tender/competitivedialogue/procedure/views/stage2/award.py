from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.award import (
    CDStage2AwardState,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Competitive Dialogue Stage 2 EU awards",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
)
class CDStage2EUTenderAwardResource(TenderAwardResource):
    state_class = CDStage2AwardState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Competitive Dialogue Stage 2 UA awards",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
)
class CDStage2UATenderAwardResource(TenderAwardResource):
    state_class = CDStage2AwardState
