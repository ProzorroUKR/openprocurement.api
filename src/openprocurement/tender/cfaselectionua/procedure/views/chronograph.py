from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender chronograph",
)
class CFASelectionChronographResource(TenderChronographResource):
    state_class = CFASelectionTenderState

