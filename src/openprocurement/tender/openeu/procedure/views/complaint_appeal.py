from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)


@resource(
    name="aboveThresholdEU:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender complaint appeals",
)
class OpenEUComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
