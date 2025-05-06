from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal_document import (
    BaseCancellationComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Cancellation Complaint Appeal Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender cancellation complaint appeal documents",
)
class CD2EUCancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaint Appeal Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender cancellation complaint appeal documents",
)
class CD2UACancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass
