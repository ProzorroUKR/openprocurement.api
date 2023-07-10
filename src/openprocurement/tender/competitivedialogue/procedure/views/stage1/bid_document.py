from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.models.bid_document import (
    PostDocument as CDPostDocument,
    PatchDocument as CDPatchDocument,
    Document as CDDocument,
)
from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)


@resource(
    name="{}:Tender Bid Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender bidder documents",
)
class TenderEUBidDocumentResource(BaseTenderBidDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument


@resource(
    name="{}:Tender Bid Eligibility Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender bidder eligibility documents",
)
class TenderEUBidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument


@resource(
    name="{}:Tender Bid Financial Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender bidder financial documents",
)
class TenderEUBidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument


@resource(
    name="{}:Tender Bid Qualification Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender bidder qualification documents",
)
class TenderEUBidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument



@resource(
    name="{}:Tender Bid Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender bidder documents",
)
class TenderUABidDocumentResource(BaseTenderBidDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument


@resource(
    name="{}:Tender Bid Eligibility Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender bidder eligibility documents",
)
class TenderUABidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument


@resource(
    name="{}:Tender Bid Financial Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender bidder financial documents",
)
class TenderUABidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument


@resource(
    name="{}:Tender Bid Qualification Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender bidder qualification documents",
)
class TenderUABidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    model_class = CDDocument
    create_model_class = CDPostDocument
    update_model_class = CDPatchDocument
