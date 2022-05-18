from openprocurement.tender.openeu.procedure.views.contract_document import OpenEUContractDocumentResource
from cornice.resource import resource


@resource(
    name="esco:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO Contract documents",
)
class ESCOContractDocumentResource(OpenEUContractDocumentResource):
    pass
