from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)


@resource(
    name="esco:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType="esco",
)
class ESCOAwardSignResource(AwardSignResource):
    context_objs = {
        "tender": ESCOTenderSerializer,
    }
