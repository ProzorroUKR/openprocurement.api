from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="{}:Tender Chronograph".format(STAGE_2_UA_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="",
)
class CDOpenUAChronographResource(TenderChronographResource):
    state_class = CDStage2UATenderState


@resource(
    name="{}:Tender Chronograph".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="",
)
class CDOpenEUChronographResource(TenderChronographResource):
    state_class = CDStage2EUTenderState
