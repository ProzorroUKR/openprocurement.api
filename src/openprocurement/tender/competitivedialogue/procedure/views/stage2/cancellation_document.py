from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource


@resource(
    name="{}:Tender Cancellation Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue stage2 EU cancellation documents",
)
class CD2EUCancellationDocumentResource(CancellationDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue stage2 UA cancellation documents",
)
class CD2UACancellationDocumentResource(CancellationDocumentResource):
    pass
