from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description="Tender award documents",
)
class PQTenderAwardDocumentResource(BaseAwardDocumentResource):
    pass
