from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.complaint_post import (
    BaseTenderComplaintPostResource,
)


@resource(
    name="complexAsset.arma:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender complaint posts",
)
class ComplaintPostResource(BaseTenderComplaintPostResource):
    pass
