from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU


@resource(
    name=f"{ABOVE_THRESHOLD_EU}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_EU,
    description="Tender qualification documents",
)
class OpenEUQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
