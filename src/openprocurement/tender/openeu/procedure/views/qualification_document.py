from openprocurement.tender.core.procedure.views.qualification_document import BaseQualificationDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender qualification documents",
)
class EUTenderQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
