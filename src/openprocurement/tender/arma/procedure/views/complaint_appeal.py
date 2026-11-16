from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender complaint appeals",
)
class ComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
