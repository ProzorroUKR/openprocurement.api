from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseTenderComplaintAppealResource,
)


@resource(
    name="complexAsset.arma:Tender Complaint Appeals",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender complaint appeals",
)
class ComplaintAppealResource(BaseTenderComplaintAppealResource):
    pass
