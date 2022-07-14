from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import Stage1TenderState
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Chronograph".format(CD_EU_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=CD_EU_TYPE,
    description="Open Contracting compatible data exchange format. See  for more info",
)
class CD1EUChronographResource(TenderChronographResource):
    state_class = Stage1TenderState


@resource(
    name="{}:Tender Chronograph".format(CD_UA_TYPE),
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=CD_UA_TYPE,
    description="Open Contracting compatible data exchange format. See # for more info",
)
class CD1UAChronographResource(TenderChronographResource):
    state_class = Stage1TenderState
