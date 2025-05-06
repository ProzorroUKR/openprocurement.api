from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE


@resource(
    name=f"{ABOVE_THRESHOLD_UA_DEFENSE}:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA_DEFENSE,
    description="Tender complaint appeals",
)
class OpenUADefenseComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
