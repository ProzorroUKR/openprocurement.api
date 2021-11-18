from openprocurement.tender.openeu.procedure.views.award_document import EUTenderBidDocumentResource
from cornice.resource import resource


@resource(
    name="esco:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO Award documents",
)
class ESCOTenderBidDocumentResource(EUTenderBidDocumentResource):
    pass
