from openprocurement.tender.core.procedure.views.award_complaint_post import BaseAwardComplaintPostResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Award Complaint Posts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender award complaint posts",
)
class CD2EUAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass


@resource(
    name="{}:Tender Award Complaint Posts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender award complaint posts",
)
class CD2UAAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
