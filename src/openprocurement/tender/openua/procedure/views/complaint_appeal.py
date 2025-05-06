from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA


@resource(
    name=f"{ABOVE_THRESHOLD_UA}:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA,
    description="Tender complaint appeals",
)
class OpenUAComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
