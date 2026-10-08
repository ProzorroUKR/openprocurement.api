from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_document import BaseQualificationDocumentResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_EU, OPEN_ROUTE_PREFIX, REQUEST_FOR_PROPOSAL


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    description="Tender qualification documents",
    procurementMethodType=[ABOVE_THRESHOLD_EU, REQUEST_FOR_PROPOSAL],
)
class OpenBaseQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
