from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name="aboveThresholdEU:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender award complaint appeals",
)
class OpenEUAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
