from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.tender.limited.procedure.state.tender_document import LimitedTenderDocumentState


@resource(
    name="reporting:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="reporting",
    description="Tender related binary files (PDFs, etc.)",
)
class ReportingTenderDocumentResource(TenderDocumentResource):
    state_class = LimitedTenderDocumentState


@resource(
    name="negotiation:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender related binary files (PDFs, etc.)",
)
class NegotiationTenderDocumentResource(ReportingTenderDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender related binary files (PDFs, etc.)",
)
class NegotiationQuickTenderDocumentResource(ReportingTenderDocumentResource):
    pass
