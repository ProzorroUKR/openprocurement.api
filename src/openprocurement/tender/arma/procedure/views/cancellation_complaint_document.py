from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource as BaseCancellationComplaintDocumentResource,
)
from openprocurement.tender.openua.procedure.state.complaint_document import (
    OpenUAComplaintDocumentState,
)


@resource(
    name="complexAsset.arma:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation complaint documents",
)
class CancellationComplaintDocumentResource(BaseCancellationComplaintDocumentResource):
    state_class = OpenUAComplaintDocumentState
