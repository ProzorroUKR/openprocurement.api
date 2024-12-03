from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.views.complaint_post import (
    BaseTenderComplaintPostResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender complaint posts",
)
class OpenComplaintPostResource(BaseTenderComplaintPostResource):
    pass
