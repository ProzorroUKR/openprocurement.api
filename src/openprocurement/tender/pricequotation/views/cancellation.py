# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation import\
    TenderCancellationResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Cancellations".format(PMT),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=PMT,
    description="Tender cancellations",
)
class PQTenderCancellationResource(TenderCancellationResource):
    """PriceQuotation cancellation"""
