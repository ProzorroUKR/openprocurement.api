# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.utils import add_next_award
from openprocurement.tender.core.views.cancellation import BaseTenderCancellationResource


@optendersresource(
    name="belowThreshold:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="belowThreshold",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseTenderCancellationResource):
    add_next_award_method = add_next_award
