from openprocurement.tender.openeu.procedure.views.bid_document import (
    OpenEUTenderBidDocumentResource,
    TenderEUBidFinancialDocumentResource,
    TenderEUBidEligibilityDocumentResource,
    TenderEUBidQualificationDocumentResource,
)
from openprocurement.tender.openua.procedure.views.bid_document import TenderUaBidDocumentResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Bid Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder documents",
)
class CompetitiveDialogueStage2EUBidDocumentResource(OpenEUTenderBidDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage2 UA bidder documents",
)
class CompetitiveDialogueStage2UaBidDocumentResource(TenderUaBidDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Financial Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder financial documents",
)
class CompetitiveDialogueStage2EUBidFinancialDocumentResource(TenderEUBidFinancialDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Eligibility Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder eligibility documents",
)
class CompetitiveDialogueStage2EUBidEligibilityDocumentResource(TenderEUBidEligibilityDocumentResource):
    pass


@resource(
    name="{}:Tender Bid Qualification Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder qualification documents",
)
class CompetitiveDialogueStage2EUBidQualificationDocumentResource(TenderEUBidQualificationDocumentResource):
    pass
