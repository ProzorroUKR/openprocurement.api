# -*- coding: utf-8 -*-

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@optendersresource(
    name="%s:Tender Cancellation Complaints" % STAGE_2_EU_TYPE,
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU cancellation complaints",
)
class CompetitiveDialogueStage2EUCancellationComplaintResource(TenderCancellationComplaintResource):
    """ TenderEU Cancellation Complaints """


@optendersresource(
    name="%s:Tender Cancellation Complaints" % STAGE_2_UA_TYPE,
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA cancellation complaints",
)
class CompetitiveDialogueStage2UACancellationComplaintResource(TenderCancellationComplaintResource):
    """ TenderUA Cancellation Complaints """
