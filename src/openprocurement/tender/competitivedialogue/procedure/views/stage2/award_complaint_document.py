from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.award_complaint_document import (
    AboveThresholdUAAwardComplaintDocumentState,
)


@resource(
    name="{}:Tender Award Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 award complaint documents",
)
class CD2EUAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = AboveThresholdUAAwardComplaintDocumentState


@resource(
    name="{}:Tender Award Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 award complaint documents",
)
class CD2UAAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = AboveThresholdUAAwardComplaintDocumentState
