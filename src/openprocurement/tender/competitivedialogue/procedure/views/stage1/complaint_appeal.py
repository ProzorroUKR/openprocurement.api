from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)


@resource(
    name="{}:Tender Complaint Appeals".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender complaint appeals",
)
class CDEUComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Complaint Appeals".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender complaint posts",
)
class CDUAComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
