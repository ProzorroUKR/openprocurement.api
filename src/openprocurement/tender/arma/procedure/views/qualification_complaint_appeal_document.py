from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource as BaseQualificationComplaintAppealDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Qualification Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender qualification complaint appeal documents",
)
class QualificationComplaintAppealDocumentResource(BaseQualificationComplaintAppealDocumentResource):
    pass
