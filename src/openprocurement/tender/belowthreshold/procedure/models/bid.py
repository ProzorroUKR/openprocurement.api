from openprocurement.tender.belowthreshold.procedure.models.document import Document, PostDocument
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchObjResponsesMixin
from openprocurement.tender.core.procedure.models.bid import (
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    Bid as BaseBid,
)
from openprocurement.tender.core.procedure.models.base import ListType
from schematics.types.compound import ModelType


class PostBid(BasePostBid, PostBidResponsesMixin):
    documents = ListType(ModelType(PostDocument, required=True))
    financialDocuments = ListType(ModelType(PostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True))
    qualificationDocuments = ListType(ModelType(PostDocument, required=True))


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    pass


class Bid(PostBidResponsesMixin, BaseBid):
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))
