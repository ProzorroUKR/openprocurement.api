from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.lot import (
    CDStage1EUTenderLotState,
    CDStage1UATenderLotState,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="{}:Tender Lots".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue EU lots",
)
class CompetitiveDialogueEULotResource(TenderLotResource):
    state_class = CDStage1EUTenderLotState


@resource(
    name="{}:Tender Lots".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA lots",
)
class CompetitiveDialogueUALotResource(TenderLotResource):
    state_class = CDStage1UATenderLotState
