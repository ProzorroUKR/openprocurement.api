from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDUAStage2TenderState,
    CDEUStage2TenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Chronograph".format(STAGE_2_UA_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="",
)
class CDOpenUAChronographResource(TenderChronographResource):
    state_class = CDUAStage2TenderState


@resource(
    name="{}:Tender Chronograph".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="",
)
class CDOpenEUChronographResource(TenderChronographResource):
    state_class = CDEUStage2TenderState

