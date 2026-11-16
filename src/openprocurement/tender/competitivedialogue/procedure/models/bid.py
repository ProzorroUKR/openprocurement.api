from openprocurement.tender.competitivedialogue.procedure.models.document import CDBidDocument, CDBidPostDocument
from openprocurement.tender.competitivedialogue.procedure.models.lot_value import (
    CDLotValue,
    CDPatchLotValue,
    CDPostLotValue,
)
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid


class CDPatchBid(PatchBid):
    lotValues: list[CDPatchLotValue] | None = None


class CDPatchQualificationBid(CDPatchBid):
    lotValues: list[CDLotValue] | None = None


class CDPostBid(PostBid):
    lotValues: list[CDPostLotValue] | None = None
    documents: list[CDBidPostDocument] | None = None
    financialDocuments: list[CDBidPostDocument] | None = None
    eligibilityDocuments: list[CDBidPostDocument] | None = None
    qualificationDocuments: list[CDBidPostDocument] | None = None


class CDBid(Bid):
    lotValues: list[CDLotValue] | None = None
    documents: list[CDBidDocument] | None = None
    financialDocuments: list[CDBidDocument] | None = None
    eligibilityDocuments: list[CDBidDocument] | None = None
    qualificationDocuments: list[CDBidDocument] | None = None
