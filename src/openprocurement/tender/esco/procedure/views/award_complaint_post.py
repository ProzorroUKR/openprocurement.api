from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)


@resource(
    name="esco:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="esco",
    description="Tender award complaint posts",
)
class ESCOAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
