# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.bid_document import TenderUaBidDocumentResource


# @optendersresource(
#     name="simple.defense:Tender Bid Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
#     procurementMethodType="simple.defense",
#     description="Tender simple.defense bidder documents",
# )
class TenderSimpleDefBidDocumentResource(TenderUaBidDocumentResource):
    pass
