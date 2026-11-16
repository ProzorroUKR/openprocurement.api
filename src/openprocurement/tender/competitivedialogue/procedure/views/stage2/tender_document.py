from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.tender_document import TenderDocumentResource
from openprocurement.tender.open.procedure.state.tender_document import (
    AboveThresholdTenderDocumentState,
    AboveThresholdUATenderDocumentState,
)


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description=f"Tender {ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2} related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2EUDocumentResource(TenderDocumentResource):
    state_class = AboveThresholdUATenderDocumentState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description=f"Tender {ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2} related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2UADocumentResource(TenderDocumentResource):
    state_class = AboveThresholdTenderDocumentState
