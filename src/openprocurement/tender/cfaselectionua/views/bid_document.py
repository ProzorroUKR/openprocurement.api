# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.bid_document import TenderBidDocumentResource


# @optendersresource(
#     name="closeFrameworkAgreementSelectionUA:Tender Bid Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
#     procurementMethodType="closeFrameworkAgreementSelectionUA",
#     description="Tender bidder documents",
# )
class TenderCFASUABidDocumentResource(TenderBidDocumentResource):
    pass
