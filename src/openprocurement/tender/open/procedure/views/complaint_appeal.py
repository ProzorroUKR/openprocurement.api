from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.complaint_appeal import BaseTenderComplaintAppealResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    description="Tender complaint appeals",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
    ],
)
class OpenBaseTenderComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
