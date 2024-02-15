from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_post import (
    BaseTenderComplaintPostResource,
)


@resource(
    name="aboveThresholdUA.defense:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender complaint posts",
)
class OpenUADefenseComplaintPostResource(BaseTenderComplaintPostResource):
    pass
