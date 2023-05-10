from openprocurement.tender.openeu.procedure.views.qualification_document import BaseQualificationDocumentResource
from cornice.resource import resource


@resource(
    name="esco:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO qualification documents",
)
class EUTenderQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
