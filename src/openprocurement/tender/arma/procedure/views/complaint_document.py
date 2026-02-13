from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


@resource(
    name="complexAsset.arma:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender complaint documents",
)
class ComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
