from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.openeu.procedure.state.lot import TenderLotState


@resource(
    name="aboveThresholdEU:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU lots",
)
class TenderEULotResource(TenderLotResource):
    state_class = TenderLotState
