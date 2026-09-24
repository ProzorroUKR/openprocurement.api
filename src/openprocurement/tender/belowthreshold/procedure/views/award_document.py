from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)


@resource(
    name="belowThreshold:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender award documents",
)
class BelowThresholdTenderBidDocumentResource(BaseAwardDocumentResource):
    pass
