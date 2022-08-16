from openprocurement.tender.openeu.procedure.views.cancellation import EUCancellationResource
from openprocurement.tender.openua.procedure.views.cancellation import UACancellationResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellations".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue stage2 UE cancellations",
)
class CD2EUDefenseCancellationResource(EUCancellationResource):
    pass


@resource(
    name="{}:Tender Cancellations".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue stage2 UA cancellations",
)
class CD2UADefenseCancellationResource(UACancellationResource):
    pass

