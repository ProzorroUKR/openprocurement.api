from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.review_request import TenderReviewRequestResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.review_request import (
    BelowThresholdReviewRequestState,
    RFPReviewRequestState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Review Request",
    collection_path="/tenders/{tender_id}/review_requests",
    path="/tenders/{tender_id}/review_requests/{review_request_id}",
    description="Tender review request",
    procurementMethodType=[ProcurementMethodType.BELOW_THRESHOLD, ProcurementMethodType.REQUEST_FOR_PROPOSAL],
)
class OpenTenderReviewRequestResource(TenderReviewRequestResource):
    state_classes = {
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdReviewRequestState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPReviewRequestState,
    }
