from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.cancellation_complaint_post_document import (
    BaseCancellationComplaintPostDocumentResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Post Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender cancellation complaint post documents",
)
class CDEUCancellationComplaintPostDocumentResource(BaseCancellationComplaintPostDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Post Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender cancellation complaint post documents",
)
class CDUACancellationComplaintPostDocumentResource(BaseCancellationComplaintPostDocumentResource):
    pass
