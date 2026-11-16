from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.tender_document import TenderDocumentResource
from openprocurement.tender.open.procedure.state.tender_document import AboveThresholdTenderDocumentState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description=f"Tender {ProcurementMethodType.COMPETITIVE_DIALOGUE_EU} related binary files (PDFs, etc.)",
)
class CDEUTenderDocumentResource(TenderDocumentResource):
    state_class = AboveThresholdTenderDocumentState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description=f"Tender {ProcurementMethodType.COMPETITIVE_DIALOGUE_UA} related binary files (PDFs, etc.)",
)
class CDUATenderDocumentResource(TenderDocumentResource):
    state_class = AboveThresholdTenderDocumentState
