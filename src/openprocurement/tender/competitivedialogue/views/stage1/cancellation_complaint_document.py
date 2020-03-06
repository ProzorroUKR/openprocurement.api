from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.cancellation_complaint_document import \
    BaseTenderComplaintCancellationDocumentResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Tender Cancellation Complaint Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender cancellation complaint documents",
)
class CompetitiveDialogueEUCancellationComplaintDocument(BaseTenderComplaintCancellationDocumentResource):
    pass


@optendersresource(
    name="{}:Tender Cancellation Complaint Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender cancellation complaint documents",
)
class CompetitiveDialogueUACancellationComplaintDocument(BaseTenderComplaintCancellationDocumentResource):
    pass
