from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="complexAsset.arma:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation complaint appeals",
)
class CancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
