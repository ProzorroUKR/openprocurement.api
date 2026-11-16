from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.bid_document import (
    CDBidDocumentState,
    CDBidFinancialDocumentState,
)
from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)


@resource(
    name="{}:Tender Bid Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender bidder documents",
)
class TenderEUBidDocumentResource(BaseTenderBidDocumentResource):
    state_class = CDBidDocumentState


@resource(
    name="{}:Tender Bid Eligibility Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender bidder eligibility documents",
)
class TenderEUBidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    state_class = CDBidDocumentState


@resource(
    name="{}:Tender Bid Financial Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender bidder financial documents",
)
class TenderEUBidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    state_class = CDBidFinancialDocumentState


@resource(
    name="{}:Tender Bid Qualification Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender bidder qualification documents",
)
class TenderEUBidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    state_class = CDBidFinancialDocumentState


@resource(
    name="{}:Tender Bid Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender bidder documents",
)
class TenderUABidDocumentResource(BaseTenderBidDocumentResource):
    state_class = CDBidDocumentState


@resource(
    name="{}:Tender Bid Eligibility Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender bidder eligibility documents",
)
class TenderUABidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    state_class = CDBidDocumentState


@resource(
    name="{}:Tender Bid Financial Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender bidder financial documents",
)
class TenderUABidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    state_class = CDBidFinancialDocumentState


@resource(
    name="{}:Tender Bid Qualification Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender bidder qualification documents",
)
class TenderUABidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    state_class = CDBidFinancialDocumentState
