from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}::Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
)
class UAAwardSignResource(AwardSignResource):
    pass
