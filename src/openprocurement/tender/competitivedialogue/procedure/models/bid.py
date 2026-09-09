from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.competitivedialogue.procedure.models.document import CDBidDocument, CDBidPostDocument
from openprocurement.tender.competitivedialogue.procedure.models.lot_value import (
    CDLotValue,
    CDPatchLotValue,
    CDPostLotValue,
)
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid


class CDPatchBid(PatchBid):
    lotValues = ListType(ModelType(CDPatchLotValue, required=True))


class CDPatchQualificationBid(CDPatchBid):
    lotValues = ListType(ModelType(CDLotValue, required=True))


class CDPostBid(PostBid):
    lotValues = ListType(ModelType(CDPostLotValue, required=True))
    documents = ListType(ModelType(CDBidPostDocument, required=True))
    financialDocuments = ListType(ModelType(CDBidPostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(CDBidPostDocument, required=True))
    qualificationDocuments = ListType(ModelType(CDBidPostDocument, required=True))

    def validate_value(self, data, value):
        pass  # stage 1 bids have no value

    def validate_parameters(self, data, parameters):
        pass  # stage 1 bids have no parameters


class CDBid(Bid):
    lotValues = ListType(ModelType(CDLotValue, required=True))

    def validate_parameters(self, data, parameters):
        pass  # stage 1 bids have no parameters

    documents = ListType(ModelType(CDBidDocument, required=True))
    financialDocuments = ListType(ModelType(CDBidDocument, required=True))
    eligibilityDocuments = ListType(ModelType(CDBidDocument, required=True))
    qualificationDocuments = ListType(ModelType(CDBidDocument, required=True))
