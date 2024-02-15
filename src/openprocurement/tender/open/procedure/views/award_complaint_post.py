from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender award complaint posts",
)
class OpenAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
