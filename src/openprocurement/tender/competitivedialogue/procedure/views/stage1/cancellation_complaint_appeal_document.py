from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal_document import (
    BaseCancellationComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Appeal Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender cancellation complaint appeal documents",
)
class CDEUCancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Appeal Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender cancellation complaint appeal documents",
)
class CDUACancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass
