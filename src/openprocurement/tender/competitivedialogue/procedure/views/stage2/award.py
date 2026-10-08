from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage2.award import (
    CDStage2AwardState,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Competitive Dialogue Stage 2 EU awards",
    procurementMethodType=STAGE_2_EU_TYPE,
)
class CDStage2EUTenderAwardResource(TenderAwardResource):
    state_class = CDStage2AwardState


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Competitive Dialogue Stage 2 UA awards",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class CDStage2UATenderAwardResource(TenderAwardResource):
    state_class = CDStage2AwardState
