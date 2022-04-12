from openprocurement.tender.openeu.procedure.views.contract_document import OpenEUContractDocumentResource
from openprocurement.tender.openua.procedure.views.contract_document import OpenUAContractDocumentResource
from cornice.resource import resource


@resource(
    name="competitiveDialogueEU.stage2:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="competitiveDialogueEU.stage2",
    description="Competitive Dialogue Stage 2 EU contract documents",
)
class CDStage2EUContractDocumentResource(OpenEUContractDocumentResource):
    pass


@resource(
    name="competitiveDialogueUA.stage2:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="competitiveDialogueUA.stage2",
    description="Competitive Dialogue Stage 2 UA contract documents",
)
class CDStage2UAContractDocumentResource(OpenUAContractDocumentResource):
    pass
