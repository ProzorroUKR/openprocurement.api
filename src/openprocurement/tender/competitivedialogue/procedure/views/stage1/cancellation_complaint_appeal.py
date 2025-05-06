from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Appeals".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender cancellation complaint appeals",
)
class CDEUCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Appeals".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender cancellation complaint posts",
)
class CDUACancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
