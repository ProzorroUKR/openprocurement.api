from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.complaint_post import BaseTenderComplaintPostResource
from cornice.resource import resource


@resource(
    name="{}:Tender Complaint Posts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender complaint posts",
)
class CD2EUComplaintPostResource(BaseTenderComplaintPostResource):
    pass


@resource(
    name="{}:Tender Complaint Posts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender complaint posts",
)
class CD2UAComplaintPostResource(BaseTenderComplaintPostResource):
    pass
