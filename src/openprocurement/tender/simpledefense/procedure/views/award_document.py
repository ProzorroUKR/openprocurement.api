from cornice.resource import resource

from openprocurement.tender.openuadefense.procedure.views.award_document import (
    UADefenseTenderAwardDocumentResource,
)


@resource(
    name="simple.defense:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="simple.defense",
    description="Tender award documents",
)
class SimpleDefenseTenderAwardDocumentResource(UADefenseTenderAwardDocumentResource):
    pass
