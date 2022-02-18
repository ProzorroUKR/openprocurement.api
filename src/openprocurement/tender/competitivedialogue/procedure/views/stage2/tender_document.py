from openprocurement.tender.openeu.procedure.views.tender_document import TenderEUDocumentResource
from openprocurement.tender.openua.procedure.views.tender_document import UATenderDocumentResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description=f"Tender {STAGE_2_EU_TYPE} related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2EUDocumentResource(TenderEUDocumentResource):
    pass


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description=f"Tender {STAGE_2_UA_TYPE} related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2UADocumentResource(UATenderDocumentResource):
    pass
