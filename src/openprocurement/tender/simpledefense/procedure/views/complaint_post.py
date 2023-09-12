from openprocurement.tender.core.procedure.views.complaint_post import BaseTenderComplaintPostResource
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="simple.defense",
    description="Tender complaint posts",
)
class SimpleDefenseComplaintPostResource(BaseTenderComplaintPostResource):
    pass
