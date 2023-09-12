from openprocurement.tender.core.procedure.views.cancellation_complaint_post_document import (
    BaseCancellationComplaintPostDocumentResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellation Complaint Post Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender cancellation complaint post documents",
)
class CD2EUCancellationComplaintPostDocumentResource(BaseCancellationComplaintPostDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Post Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender cancellation complaint post documents",
)
class CD2UACancellationComplaintPostDocumentResource(BaseCancellationComplaintPostDocumentResource):
    pass
