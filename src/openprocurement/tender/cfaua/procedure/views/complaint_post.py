from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_post import (
    CFAUAComplaintPostState,
)
from openprocurement.tender.core.procedure.views.complaint_post import (
    BaseTenderComplaintPostResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender complaint posts",
)
class CFAUAComplaintPostResource(BaseTenderComplaintPostResource):
    state_class = CFAUAComplaintPostState
