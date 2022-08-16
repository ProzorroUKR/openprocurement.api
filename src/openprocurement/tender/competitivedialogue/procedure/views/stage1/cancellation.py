from openprocurement.tender.openeu.procedure.views.cancellation import EUCancellationResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellations".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue UE cancellations",
)
class CDEUDefenseCancellationResource(EUCancellationResource):
    pass


@resource(
    name="{}:Tender Cancellations".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellations",
)
class CDUADefenseCancellationResource(EUCancellationResource):
    pass

