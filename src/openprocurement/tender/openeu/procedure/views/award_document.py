from openprocurement.tender.openua.procedure.views.award_document import UATenderAwardDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender award documents",
)
class EUTenderBidDocumentResource(UATenderAwardDocumentResource):
    pass
