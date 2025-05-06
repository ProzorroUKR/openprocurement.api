from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender award complaint appeals",
)
class COAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
