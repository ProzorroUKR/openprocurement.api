"""
Registry of tender procedures: procurementMethodType → the core model classes the procedure uses.

All tender models live in ``openprocurement.tender.core.procedure.models``; procedure-specific variants are
prefixed classes (``ESCOPostTender``, ``LimitedAward`` ...). This registry is the single place that says which
variant belongs to which procedure, so that state classes (and, later, views) can resolve models by
``procurementMethodType`` instead of importing them statically.
"""

from dataclasses import dataclass
from typing import Optional, Type

from openprocurement.api.procedure.models.base import Model
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.models.agreement import (
    CFAAgreement,
    CFAPatchAgreement,
    CFASelectionAgreement,
    CFASelectionPatchAgreement,
)
from openprocurement.tender.core.procedure.models.award import (
    ARMAAward,
    ARMAPostAward,
    Award,
    CDAward,
    CDPatchAward,
    CDPostAward,
    ESCOAward,
    ESCOPostAward,
    LimitedAward,
    LimitedPatchAward,
    LimitedPostAward,
    PatchAward,
    PostAward,
    ReportingAward,
    ReportingPatchAward,
    ReportingPostAward,
)
from openprocurement.tender.core.procedure.models.bid import (
    ARMABid,
    ARMAPatchBid,
    ARMAPatchQualificationBid,
    ARMAPostBid,
    Bid,
    CDBid,
    CDPatchBid,
    CDPatchQualificationBid,
    CDPostBid,
    CFASelectionBid,
    CFASelectionPatchBid,
    CFASelectionPatchQualificationBid,
    CFASelectionPostBid,
    ESCOBid,
    ESCOPatchBid,
    ESCOPatchQualificationBid,
    ESCOPostBid,
    PatchBid,
    PatchQualificationBid,
    PostBid,
)
from openprocurement.tender.core.procedure.models.lot import (
    ARMALot,
    ARMAPatchLot,
    ARMAPostLot,
    CFASelectionLot,
    CFASelectionPatchLot,
    CFASelectionPostLot,
    ESCOLot,
    ESCOPatchLot,
    ESCOPostLot,
    LimitedLot,
    LimitedPatchLot,
    LimitedPostLot,
    Lot,
    PatchLot,
    PostLot,
)
from openprocurement.tender.core.procedure.models.tender import (
    ARMAPatchTender,
    ARMAPostTender,
    ARMATender,
    CDStage1EUPatchTender,
    CDStage1EUPostTender,
    CDStage1EUTender,
    CDStage1UAPatchTender,
    CDStage1UAPostTender,
    CDStage1UATender,
    CDStage2EUPatchTender,
    CDStage2EUPostTender,
    CDStage2EUTender,
    CDStage2UAPatchTender,
    CDStage2UAPostTender,
    CDStage2UATender,
    CFAPatchTender,
    CFAPostTender,
    CFASelectionPatchTender,
    CFASelectionPostTender,
    CFASelectionTender,
    CFATender,
    ESCOPatchTender,
    ESCOPostTender,
    ESCOTender,
    NegotiationPatchTender,
    NegotiationPostTender,
    NegotiationQuickPatchTender,
    NegotiationQuickPostTender,
    NegotiationQuickTender,
    NegotiationTender,
    PatchTender,
    PostTender,
    PQPatchTender,
    PQPostTender,
    PQTender,
    ReportingPatchTender,
    ReportingPostTender,
    ReportingTender,
    Tender,
)
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE

ModelClass = Type[Model]


@dataclass(frozen=True)
class ProcedureModels:
    """Model classes (POST / PATCH / stored) of one procedure; ``None`` means the procedure has no such entity."""

    tender_post: ModelClass
    tender_patch: ModelClass
    tender: ModelClass

    bid_post: Optional[ModelClass] = PostBid
    bid_patch: Optional[ModelClass] = PatchBid
    bid_patch_qualification: Optional[ModelClass] = PatchQualificationBid
    bid: Optional[ModelClass] = Bid

    award_post: Optional[ModelClass] = PostAward
    award_patch: Optional[ModelClass] = PatchAward
    award: Optional[ModelClass] = Award

    lot_post: Optional[ModelClass] = PostLot
    lot_patch: Optional[ModelClass] = PatchLot
    lot: Optional[ModelClass] = Lot

    agreement_patch: Optional[ModelClass] = None
    agreement: Optional[ModelClass] = None


CORE_TENDER_MODELS = ProcedureModels(tender_post=PostTender, tender_patch=PatchTender, tender=Tender)

LIMITED_LOT_MODELS = {"lot_post": LimitedPostLot, "lot_patch": LimitedPatchLot, "lot": LimitedLot}
LIMITED_AWARD_MODELS = {"award_post": LimitedPostAward, "award_patch": LimitedPatchAward, "award": LimitedAward}

PROCEDURE_MODELS: dict[str, ProcedureModels] = {
    BELOW_THRESHOLD: CORE_TENDER_MODELS,
    REQUEST_FOR_PROPOSAL: CORE_TENDER_MODELS,
    ABOVE_THRESHOLD: CORE_TENDER_MODELS,
    ABOVE_THRESHOLD_UA: CORE_TENDER_MODELS,
    ABOVE_THRESHOLD_EU: CORE_TENDER_MODELS,
    ABOVE_THRESHOLD_UA_DEFENSE: CORE_TENDER_MODELS,
    SIMPLE_DEFENSE: CORE_TENDER_MODELS,
    COMPETITIVE_ORDERING: CORE_TENDER_MODELS,
    PQ: ProcedureModels(
        tender_post=PQPostTender,
        tender_patch=PQPatchTender,
        tender=PQTender,
        lot_post=None,
        lot_patch=None,
        lot=None,
    ),
    ESCO: ProcedureModels(
        tender_post=ESCOPostTender,
        tender_patch=ESCOPatchTender,
        tender=ESCOTender,
        bid_post=ESCOPostBid,
        bid_patch=ESCOPatchBid,
        bid_patch_qualification=ESCOPatchQualificationBid,
        bid=ESCOBid,
        award_post=ESCOPostAward,
        award=ESCOAward,
        lot_post=ESCOPostLot,
        lot_patch=ESCOPatchLot,
        lot=ESCOLot,
    ),
    COMPLEX_ASSET_ARMA: ProcedureModels(
        tender_post=ARMAPostTender,
        tender_patch=ARMAPatchTender,
        tender=ARMATender,
        bid_post=ARMAPostBid,
        bid_patch=ARMAPatchBid,
        bid_patch_qualification=ARMAPatchQualificationBid,
        bid=ARMABid,
        award_post=ARMAPostAward,
        award=ARMAAward,
        lot_post=ARMAPostLot,
        lot_patch=ARMAPatchLot,
        lot=ARMALot,
    ),
    CFA_UA: ProcedureModels(
        tender_post=CFAPostTender,
        tender_patch=CFAPatchTender,
        tender=CFATender,
        agreement_patch=CFAPatchAgreement,
        agreement=CFAAgreement,
    ),
    CFA_SELECTION: ProcedureModels(
        tender_post=CFASelectionPostTender,
        tender_patch=CFASelectionPatchTender,
        tender=CFASelectionTender,
        bid_post=CFASelectionPostBid,
        bid_patch=CFASelectionPatchBid,
        bid_patch_qualification=CFASelectionPatchQualificationBid,
        bid=CFASelectionBid,
        lot_post=CFASelectionPostLot,
        lot_patch=CFASelectionPatchLot,
        lot=CFASelectionLot,
        agreement_patch=CFASelectionPatchAgreement,
        agreement=CFASelectionAgreement,
    ),
    REPORTING: ProcedureModels(
        tender_post=ReportingPostTender,
        tender_patch=ReportingPatchTender,
        tender=ReportingTender,
        bid_post=None,
        bid_patch=None,
        bid_patch_qualification=None,
        bid=None,
        award_post=ReportingPostAward,
        award_patch=ReportingPatchAward,
        award=ReportingAward,
        **LIMITED_LOT_MODELS,
    ),
    NEGOTIATION: ProcedureModels(
        tender_post=NegotiationPostTender,
        tender_patch=NegotiationPatchTender,
        tender=NegotiationTender,
        bid_post=None,
        bid_patch=None,
        bid_patch_qualification=None,
        bid=None,
        **LIMITED_AWARD_MODELS,
        **LIMITED_LOT_MODELS,
    ),
    NEGOTIATION_QUICK: ProcedureModels(
        tender_post=NegotiationQuickPostTender,
        tender_patch=NegotiationQuickPatchTender,
        tender=NegotiationQuickTender,
        bid_post=None,
        bid_patch=None,
        bid_patch_qualification=None,
        bid=None,
        **LIMITED_AWARD_MODELS,
        **LIMITED_LOT_MODELS,
    ),
    CD_EU_TYPE: ProcedureModels(
        tender_post=CDStage1EUPostTender,
        tender_patch=CDStage1EUPatchTender,
        tender=CDStage1EUTender,
        bid_post=CDPostBid,
        bid_patch=CDPatchBid,
        bid_patch_qualification=CDPatchQualificationBid,
        bid=CDBid,
        award_post=None,
        award_patch=None,
        award=None,
    ),
    CD_UA_TYPE: ProcedureModels(
        tender_post=CDStage1UAPostTender,
        tender_patch=CDStage1UAPatchTender,
        tender=CDStage1UATender,
        bid_post=CDPostBid,
        bid_patch=CDPatchBid,
        bid_patch_qualification=CDPatchQualificationBid,
        bid=CDBid,
        award_post=None,
        award_patch=None,
        award=None,
    ),
    STAGE_2_EU_TYPE: ProcedureModels(
        tender_post=CDStage2EUPostTender,
        tender_patch=CDStage2EUPatchTender,
        tender=CDStage2EUTender,
        award_post=CDPostAward,
        award_patch=CDPatchAward,
        award=CDAward,
        lot_post=None,
        lot_patch=None,
        lot=None,
    ),
    STAGE_2_UA_TYPE: ProcedureModels(
        tender_post=CDStage2UAPostTender,
        tender_patch=CDStage2UAPatchTender,
        tender=CDStage2UATender,
        award_post=CDPostAward,
        award_patch=CDPatchAward,
        award=CDAward,
        lot_post=None,
        lot_patch=None,
        lot=None,
    ),
}


def get_procedure_models(procurement_method_type: str) -> ProcedureModels:
    try:
        return PROCEDURE_MODELS[procurement_method_type]
    except KeyError:
        raise KeyError(f"Unknown procurementMethodType: {procurement_method_type}") from None
