from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender bidder documents",
)
class BidDocumentResource(BaseTenderBidDocumentResource):
    pass


@resource(
    name="complexAsset.arma:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender bidder eligibility documents",
)
class BidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    pass


@resource(
    name="complexAsset.arma:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender bidder financial documents",
)
class BidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    pass


@resource(
    name="complexAsset.arma:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender bidder qualification documents",
)
class BidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    pass
