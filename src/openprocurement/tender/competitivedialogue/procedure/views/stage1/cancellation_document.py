from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource


@resource(
    name="{}:Tender Cancellation Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue  EU cancellation documents",
)
class CDEUCancellationDocumentResource(CancellationDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellation documents",
)
class CDUACancellationDocumentResource(CancellationDocumentResource):
    pass
