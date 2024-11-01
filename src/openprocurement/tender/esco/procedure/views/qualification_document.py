from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)
from openprocurement.tender.esco.constants import ESCO


@resource(
    name=f"{ESCO}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ESCO,
    description="Tender qualification documents",
)
class ESCOQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
