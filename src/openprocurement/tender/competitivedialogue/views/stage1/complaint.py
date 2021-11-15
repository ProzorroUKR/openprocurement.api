# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource, TenderEUClaimResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)


@optendersresource(
    name="{}:Tender Complaints Get".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue EU complaints get",
)
class CompetitiveDialogueEUComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="{}:Tender Complaints".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue EU complaints",
)
class CompetitiveDialogueEUComplaintResource(TenderEUComplaintResource):
    """ """


@optendersresource(
    name="{}:Tender Claims".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue EU claims",
)
class CompetitiveDialogueEUClaimResource(TenderEUClaimResource):
    """ """


@optendersresource(
    name="{}:Tender Complaints Get".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue UA complaints get",
)
class CompetitiveDialogueUAComplaintGetResource(BaseComplaintGetResource):
    """ """

@optendersresource(
    name="{}:Tender Complaints".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue UA complaints",
)
class CompetitiveDialogueUAComplaintResource(TenderEUComplaintResource):
    """ """


@optendersresource(
    name="{}:Tender Claims".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue UA claims",
)
class CompetitiveDialogueUAClaimResource(TenderEUClaimResource):
    """ """
