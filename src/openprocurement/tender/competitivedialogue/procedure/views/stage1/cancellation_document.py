from openprocurement.tender.openeu.procedure.views.cancellation_document import EUCancellationDocumentResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellation Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue  EU cancellation documents",
)
class CDEUCancellationDocumentResource(EUCancellationDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellation documents",
)
class CDUACancellationDocumentResource(EUCancellationDocumentResource):
    pass
