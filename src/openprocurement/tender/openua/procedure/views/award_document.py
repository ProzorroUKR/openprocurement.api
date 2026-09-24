from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)


@resource(
    name="aboveThresholdUA:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender award documents",
)
class UATenderAwardDocumentResource(BaseAwardDocumentResource):
    pass
