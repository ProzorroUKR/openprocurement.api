from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)


@resource(
    name="{}:Tender Documents".format(ProcurementMethodType.PRICE_QUOTATION),
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description="Tender related binary files (PDFs, etc.)",
)
class PQTenderDocumentResource(TenderDocumentResource):
    pass
