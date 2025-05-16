from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA


@resource(
    name=f"{ABOVE_THRESHOLD_UA}:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA,
    description="Tender award complaint appeals",
)
class OpenUAAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
