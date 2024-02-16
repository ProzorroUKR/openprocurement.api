from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_post import (
    BaseTenderComplaintPostResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender complaint posts",
)
class OpenComplaintPostResource(BaseTenderComplaintPostResource):
    pass
