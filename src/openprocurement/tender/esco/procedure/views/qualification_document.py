from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name=f"{ProcurementMethodType.ESCO}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.ESCO,
    description="Tender qualification documents",
)
class ESCOQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
