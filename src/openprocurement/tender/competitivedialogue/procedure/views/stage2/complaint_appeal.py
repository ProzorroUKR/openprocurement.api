from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)


@resource(
    name="{}:Tender Complaint Appeals".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender complaint appeals",
)
class CD2EUComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Complaint Appeals".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender complaint posts",
)
class CD2UAComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
