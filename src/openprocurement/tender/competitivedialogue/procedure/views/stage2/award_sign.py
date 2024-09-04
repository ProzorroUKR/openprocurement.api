from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.award_sign import AwardSignResource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType=STAGE_2_EU_TYPE,
)
class CDStage2EUAwardSignResource(AwardSignResource):
    pass


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Award Sign",
    path="/tenders/{tender_id}/awards/{award_id}/sign",
    description="Tender award sign",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class CDStage2UAAwardSignResource(AwardSignResource):
    pass
