from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender qualification documents",
)
class QualificationDocumentResource(BaseQualificationDocumentResource):
    pass
