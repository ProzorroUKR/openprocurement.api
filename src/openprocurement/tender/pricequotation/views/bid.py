# -*- coding: utf-8 -*-

from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.bid import\
    TenderBidResource as BaseTenderBidResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Bids".format(PMT),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=PMT,
    description="Tender bids",
)
class TenderBidResource(BaseTenderBidResource):
    """ PriceQuotation tender bid resource """
