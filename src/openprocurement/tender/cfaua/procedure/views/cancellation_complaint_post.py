from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint posts",
)
class CFAUACancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
