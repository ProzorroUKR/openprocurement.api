from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE


@resource(
    name=f"{SIMPLE_DEFENSE}:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=SIMPLE_DEFENSE,
    description="Tender complaint appeals",
)
class SimpleDefenseComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
