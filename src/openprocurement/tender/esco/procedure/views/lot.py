from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.esco.procedure.state.lot import TenderLotState


@resource(
    name="esco:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="esco",
    description="Tender ESCO lots",
)
class ESCOLotResource(TenderLotResource):
    state_class = TenderLotState
