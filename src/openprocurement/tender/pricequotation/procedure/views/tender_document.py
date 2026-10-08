from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name="{}:Tender Documents".format(PQ),
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=PQ,
    description="Tender related binary files (PDFs, etc.)",
)
class PQTenderDocumentResource(TenderDocumentResource):
    pass
