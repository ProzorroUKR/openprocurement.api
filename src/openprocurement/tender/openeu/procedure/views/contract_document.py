from openprocurement.tender.openua.procedure.views.contract_document import OpenUAContractDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender contract documents",
)
class OpenEUContractDocumentResource(OpenUAContractDocumentResource):
    pass
