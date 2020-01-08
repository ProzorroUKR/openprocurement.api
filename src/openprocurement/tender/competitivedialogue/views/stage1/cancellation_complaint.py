# -*- coding: utf-8 -*-

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Tender Cancellation Complaints".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU cancellation complaints",
)
class CompetitiveDialogueEUCancellationDocumentResource(TenderCancellationComplaintResource):
    """ Cancellation Complaint """

    pass


@optendersresource(
    name="{}:Tender Cancellation Complaints".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellation complaints",
)
class CompetitiveDialogueUACancellationDocumentResource(TenderCancellationComplaintResource):
    """ Cancellation Complaint """

    pass
