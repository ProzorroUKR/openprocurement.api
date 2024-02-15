from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.complaint_post import (
    BaseTenderComplaintPostResource,
)


@resource(
    name="{}:Tender Complaint Posts".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender complaint posts",
)
class CDEUComplaintPostResource(BaseTenderComplaintPostResource):
    pass


@resource(
    name="{}:Tender Complaint Posts".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender complaint posts",
)
class CDUAComplaintPostResource(BaseTenderComplaintPostResource):
    pass
