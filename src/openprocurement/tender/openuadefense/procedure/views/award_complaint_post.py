from openprocurement.tender.core.procedure.views.award_complaint_post import BaseAwardComplaintPostResource
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender award complaint posts",
)
class OpenUADefenseAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
