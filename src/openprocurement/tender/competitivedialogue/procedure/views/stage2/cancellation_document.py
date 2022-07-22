from openprocurement.tender.openeu.procedure.views.cancellation_document import EUCancellationDocumentResource
from openprocurement.tender.openua.procedure.views.cancellation_document import UACancellationDocumentResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellation Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue stage2 EU cancellation documents",
)
class CD2EUCancellationDocumentResource(EUCancellationDocumentResource):
    pass


@resource(
    name="{}:Tender Cancellation Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue stage2 UA cancellation documents",
)
class CD2UACancellationDocumentResource(UACancellationDocumentResource):
    pass
