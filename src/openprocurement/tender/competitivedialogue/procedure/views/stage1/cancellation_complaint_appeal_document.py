from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal_document import (
    BaseCancellationComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Appeal Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender cancellation complaint appeal documents",
)
class CDEUCancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Appeal Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender cancellation complaint appeal documents",
)
class CDUACancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass
