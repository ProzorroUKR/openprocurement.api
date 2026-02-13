from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender complaint appeal documents",
)
class ComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
