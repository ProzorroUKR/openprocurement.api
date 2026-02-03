from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)


@resource(
    name="complexAsset.arma:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation complaint posts",
)
class CancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
