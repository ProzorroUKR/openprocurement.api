from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)
from openprocurement.tender.esco.constants import ESCO


@resource(
    name=f"{ESCO}:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ESCO,
    description="Tender complaint appeals",
)
class ESCOComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
