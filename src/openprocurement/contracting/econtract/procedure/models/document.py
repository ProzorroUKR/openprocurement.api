from schematics.types import StringType

from openprocurement.contracting.core.procedure.models.document import (
    Document as BaseDocument,
)
from openprocurement.contracting.core.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.contracting.core.procedure.models.document import (
    PostDocument as BasePostDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    BaseDocument as BaseTenderDocument,
)

DOCUMENT_TYPES = (
    "tenderNotice",
    "awardNotice",
    "contractNotice",
    "notice",
    "biddingDocuments",
    "technicalSpecifications",
    "evaluationCriteria",
    "clarifications",
    "shortlistedFirms",
    "riskProvisions",
    "billOfQuantity",
    "bidders",
    "conflictOfInterest",
    "debarments",
    "evaluationReports",
    "winningBid",
    "complaints",
    "contractSigned",
    "contractArrangements",
    "contractSchedule",
    "contractAnnexe",
    "contractGuarantees",
    "subContract",
    "eligibilityCriteria",
    "contractProforma",
    "commercialProposal",
    "qualificationDocuments",
    "eligibilityDocuments",
    "registerExtract",
    "registerFiscal",
    "winningBid",
    "evidence",
    "register",
    "contractSignature",
)


class PostDocument(BasePostDocument):
    documentType = StringType(choices=DOCUMENT_TYPES)


class PatchDocument(BasePatchDocument):
    documentType = StringType(choices=DOCUMENT_TYPES)


class Document(BaseDocument):
    documentType = StringType(choices=DOCUMENT_TYPES)
    author = StringType()


class BaseChangeDocument(BaseTenderDocument):
    documentOf = StringType(default="change")
    documentType = StringType(choices=DOCUMENT_TYPES)

    def validate_relatedItem(self, data, related_item):
        pass


class PostChangeDocument(BaseChangeDocument, PostDocument):
    pass


class ChangeDocument(BaseChangeDocument, Document):
    pass
