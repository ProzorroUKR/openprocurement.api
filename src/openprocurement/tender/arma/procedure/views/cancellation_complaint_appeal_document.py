from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal_document import (
    BaseCancellationComplaintAppealDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Cancellation Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation complaint appeal documents",
)
class CancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass
