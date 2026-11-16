from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name=f"{ProcurementMethodType.COMPLEX_ASSET_ARMA}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPLEX_ASSET_ARMA,
    description="Tender qualification documents",
)
class QualificationDocumentResource(BaseQualificationDocumentResource):
    pass
