from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaselectionua.procedure.state.lot import CFASelectionTenderLotState
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    description="Tender lots",
)
class CFASelectionUATenderLotResource(TenderLotResource):
    state_class = CFASelectionTenderLotState
