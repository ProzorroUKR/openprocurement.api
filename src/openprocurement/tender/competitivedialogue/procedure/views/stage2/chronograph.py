from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="{}:Tender Chronograph".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="",
)
class CDOpenUAChronographResource(TenderChronographResource):
    state_class = CDStage2UATenderState


@resource(
    name="{}:Tender Chronograph".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="",
)
class CDOpenEUChronographResource(TenderChronographResource):
    state_class = CDStage2EUTenderState
