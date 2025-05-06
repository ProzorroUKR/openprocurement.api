from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal import (
    CFAUAComplaintAppealState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint appeals",
)
class CFAUACancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    state_class = CFAUAComplaintAppealState
