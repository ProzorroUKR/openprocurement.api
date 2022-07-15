from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.openuadefense.procedure.state.lot import TenderLotState


@resource(
    name="aboveThresholdUA.defense:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender Ua lots",
)
class OpenUADefenseLotResource(TenderLotResource):
    state_class = TenderLotState
