from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE


@resource(
    name=f"{SIMPLE_DEFENSE}:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=SIMPLE_DEFENSE,
    description="Tender award complaint appeals",
)
class SimpleDefenseAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
