from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name="{}:Tender Award Complaint Appeals".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender award complaint appeals",
)
class CD2EUAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Award Complaint Appeals".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender award complaint appeals",
)
class CD2UAAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
