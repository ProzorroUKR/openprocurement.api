from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name="complexAsset.arma:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award complaint appeals",
)
class AwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
