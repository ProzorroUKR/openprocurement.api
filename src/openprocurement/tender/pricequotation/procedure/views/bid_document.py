# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.procedure.views.bid_document import BelowThresholdTenderBidDocumentResource
from openprocurement.tender.pricequotation.constants import PMT
from cornice.resource import resource


@resource(
    name="{}:Tender Bid Documents".format(PMT),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender bidder documents",
)
class PQBidDocumentResource(BelowThresholdTenderBidDocumentResource):
    pass
