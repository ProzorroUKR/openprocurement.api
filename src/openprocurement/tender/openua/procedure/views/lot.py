from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.openua.procedure.state.lot import TenderLotState


@resource(
    name="aboveThresholdUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender Ua lots",
)
class TenderUALotResource(TenderLotResource):
    state_class = TenderLotState
