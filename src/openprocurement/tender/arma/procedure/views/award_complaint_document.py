from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource as BaseAwardComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.award_complaint_document import (
    AboveThresholdUAAwardComplaintDocumentState,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender award complaint documents",
)
class AwardComplaintDocumentResource(BaseAwardComplaintDocumentResource):
    state_class = AboveThresholdUAAwardComplaintDocumentState
