from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender chronograph",
)
class CFAUAChronographResource(TenderChronographResource):
    state_class = CFAUATenderState
