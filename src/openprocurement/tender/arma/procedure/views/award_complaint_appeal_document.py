from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.award_complaint_appeal_document import (
    BaseAwardComplaintAppealDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Award Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award complaint appeal documents",
)
class AwardComplaintAppealDocumentResource(BaseAwardComplaintAppealDocumentResource):
    pass
