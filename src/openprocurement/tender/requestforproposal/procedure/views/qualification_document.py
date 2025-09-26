from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL


@resource(
    name=f"{REQUEST_FOR_PROPOSAL}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=REQUEST_FOR_PROPOSAL,
    description="Tender qualification documents",
)
class RequestForProposalQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
