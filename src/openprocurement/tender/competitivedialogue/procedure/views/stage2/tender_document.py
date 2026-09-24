from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.tender_document import TenderDocumentResource
from openprocurement.tender.open.procedure.state.tender_document import (
    AboveThresholdTenderDocumentState,
    AboveThresholdUATenderDocumentState,
)


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description=f"Tender {STAGE_2_EU_TYPE} related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2EUDocumentResource(TenderDocumentResource):
    state_class = AboveThresholdUATenderDocumentState


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description=f"Tender {STAGE_2_UA_TYPE} related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2UADocumentResource(TenderDocumentResource):
    state_class = AboveThresholdTenderDocumentState
