from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage1.lot import TenderLotState


@resource(
    name="{}:Tender Lots".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU lots",
)
class CompetitiveDialogueEULotResource(TenderLotResource):
    state_class = TenderLotState


@resource(
    name="{}:Tender Lots".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA lots",
)
class CompetitiveDialogueUALotResource(TenderLotResource):
    state_class = TenderLotState

