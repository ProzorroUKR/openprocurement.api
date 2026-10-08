from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_document import BaseAwardDocumentResource
from openprocurement.tender.open.constants import OPEN_PROCUREMENT_METHOD_TYPES, OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    description="Tender award documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseAwardDocumentResource(BaseAwardDocumentResource):
    pass
