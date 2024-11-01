from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_post import (
    CFAUAComplaintPostState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint posts",
)
class CFAUACancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    state_class = CFAUAComplaintPostState
