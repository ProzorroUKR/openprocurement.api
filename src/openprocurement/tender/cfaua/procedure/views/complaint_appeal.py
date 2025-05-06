from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal import (
    CFAUAComplaintAppealState,
)
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender complaint posts",
)
class CFAUAComplaintAppealResource(BaseTenderComplaintAppealResource):
    state_class = CFAUAComplaintAppealState
