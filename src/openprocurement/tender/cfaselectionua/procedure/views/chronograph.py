from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    description="Tender chronograph",
)
class CFASelectionChronographResource(TenderChronographResource):
    state_class = CFASelectionTenderState
