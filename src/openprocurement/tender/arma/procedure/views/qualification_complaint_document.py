from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.qualification_complaint_document import (
    QualificationComplaintDocumentResource as BaseQualificationComplaintDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Qualification Complaint Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender qualification complaint documents",
)
class QualificationComplaintDocumentResource(BaseQualificationComplaintDocumentResource):
    pass
