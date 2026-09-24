from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender award documents",
)
class UATenderAwardDocumentResource(BaseAwardDocumentResource):
    pass
