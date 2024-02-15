from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)


@resource(
    name="aboveThresholdEU:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender award complaint posts",
)
class OpenEUAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
