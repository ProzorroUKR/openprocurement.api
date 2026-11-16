from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="{}:Tender Chronograph".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Open Contracting compatible data exchange format. See  for more info",
)
class CD1EUChronographResource(TenderChronographResource):
    state_class = CDStage1TenderState


@resource(
    name="{}:Tender Chronograph".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Open Contracting compatible data exchange format. See # for more info",
)
class CD1UAChronographResource(TenderChronographResource):
    state_class = CDStage1TenderState
