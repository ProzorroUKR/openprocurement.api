from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender chronograph",
)
class CFAUAChronographResource(TenderChronographResource):
    state_class = CFAUATenderState

