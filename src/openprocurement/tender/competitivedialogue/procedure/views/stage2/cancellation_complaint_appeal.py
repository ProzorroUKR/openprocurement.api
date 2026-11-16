from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Appeals".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Tender cancellation complaint appeals",
)
class CD2EUCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Appeals".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Tender cancellation complaint posts",
)
class CD2UACancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
