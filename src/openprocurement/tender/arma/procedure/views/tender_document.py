from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.openua.procedure.views.tender_document import (
    UATenderDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender related binary files (PDFs, etc.)",
)
class DocumentResource(UATenderDocumentResource):
    pass
