from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Chronograph".format(STAGE_2_UA_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="",
)
class CDOpenUAChronographResource(TenderChronographResource):
    state_class = OpenUATenderState


@resource(
    name="{}:Tender Chronograph".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="",
)
class CDOpenEUChronographResource(TenderChronographResource):
    state_class = BaseOpenEUTenderState

