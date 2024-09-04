from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType=PQ,
)
class PQAwardSignResource(AwardSignResource):
    pass
