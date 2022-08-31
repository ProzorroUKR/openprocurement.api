from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.lot import TenderLotState


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender lots",
)
class TenderUALotResource(TenderLotResource):
    state_class = TenderLotState
