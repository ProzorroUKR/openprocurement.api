from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource as BaseAwardComplaintDocumentResource,
)
from openprocurement.tender.openua.procedure.state.award_complaint_document import (
    OpenUAAwardComplaintDocumentState,
)


@resource(
    name="complexAsset.arma:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award complaint documents",
)
class AwardComplaintDocumentResource(BaseAwardComplaintDocumentResource):
    state_class = OpenUAAwardComplaintDocumentState
