from openprocurement.tender.openua.procedure.views.award_document import UATenderAwardDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender award documents",
)
class UADefenseTenderAwardDocumentResource(UATenderAwardDocumentResource):
    pass
