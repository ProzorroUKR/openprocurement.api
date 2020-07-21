# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_document import\
    TenderBidDocumentResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Bid Documents".format(PMT),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender bidder documents",
)
class PQTenderBidDocumentResource(TenderBidDocumentResource):
    pass
