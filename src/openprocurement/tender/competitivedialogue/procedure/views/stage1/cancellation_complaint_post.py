from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellation Complaint Posts".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender cancellation complaint posts",
)
class CDEUCancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Posts".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender cancellation complaint posts",
)
class CDUACancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
