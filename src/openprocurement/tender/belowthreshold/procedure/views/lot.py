from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.lot import TenderLotState
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="belowThreshold:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="belowThreshold",
    description="Tender lots",
)
class BelowThresholdTenderLotResource(TenderLotResource):
    state_class = TenderLotState
