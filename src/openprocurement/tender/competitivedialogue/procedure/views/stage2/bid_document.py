from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)


@resource(
    name="{}:Tender Bid Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender bidder documents",
)
class TenderEUBidDocumentResource(BaseTenderBidDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Eligibility Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender bidder eligibility documents",
)
class TenderEUBidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Financial Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender bidder financial documents",
)
class TenderEUBidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Qualification Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender bidder qualification documents",
)
class TenderEUBidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender bidder documents",
)
class TenderUABidDocumentResource(BaseTenderBidDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Eligibility Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender bidder eligibility documents",
)
class TenderUABidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Financial Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender bidder financial documents",
)
class TenderUABidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Qualification Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender bidder qualification documents",
)
class TenderUABidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    pass
