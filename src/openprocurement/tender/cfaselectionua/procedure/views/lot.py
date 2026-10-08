from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.lot import CFASelectionTenderLotState
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender lots",
)
class CFASelectionUATenderLotResource(TenderLotResource):
    state_class = CFASelectionTenderLotState
