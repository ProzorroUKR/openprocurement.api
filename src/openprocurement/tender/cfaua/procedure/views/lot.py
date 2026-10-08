from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.lot import CFAUATenderLotState
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="closeFrameworkAgreementUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU lots",
)
class CFAUATenderLotResource(TenderLotResource):
    state_class = CFAUATenderLotState
