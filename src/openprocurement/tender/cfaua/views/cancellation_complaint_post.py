# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation_complaint_post import (
    TenderCancellationComplaintPostResource as BaseTenderCancellationComplaintPostResource,
)


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint posts",
)
class TenderCancellationComplaintPostResource(BaseTenderCancellationComplaintPostResource):
    pass
