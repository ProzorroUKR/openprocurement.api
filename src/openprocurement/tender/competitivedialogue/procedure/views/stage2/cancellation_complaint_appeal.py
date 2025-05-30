from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Appeals".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender cancellation complaint appeals",
)
class CD2EUCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Appeals".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender cancellation complaint posts",
)
class CD2UACancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
