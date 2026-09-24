from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=PQ,
    description="Tender award documents",
)
class PQTenderAwardDocumentResource(BaseAwardDocumentResource):
    pass
