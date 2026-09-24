from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.lot import (
    CDStage2EUTenderLotState,
    CDStage2UATenderLotState,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="{}:Lots".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender stage2 EU lots",
)
class TenderStage2EULotResource(TenderLotResource):
    state_class = CDStage2EUTenderLotState


@resource(
    name="{}:Lots".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender stage2 UA lots",
)
class TenderStage2UALotResource(TenderLotResource):
    state_class = CDStage2UATenderLotState
