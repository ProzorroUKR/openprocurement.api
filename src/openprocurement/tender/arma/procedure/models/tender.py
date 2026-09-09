from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.models.lot import ARMALot, ARMAPatchTenderLot, ARMAPostTenderLot
from openprocurement.tender.core.constants import AWARD_CRITERIA_CHOICES
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PatchTenderPeriodsMixin,
    PostTenderItemsMixin,
    PostTenderPeriodsMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderPeriodsMixin,
    TenderSubmissionMixin,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender


class ARMAPostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderPeriodsMixin,
    PostTenderItemsMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    procurementMethodType = StringType(choices=[COMPLEX_ASSET_ARMA], default=COMPLEX_ASSET_ARMA)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(ARMAPostTenderLot, required=True), validators=[validate_uniq_id])

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class ARMAPatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderPeriodsMixin,
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procuringEntity = ModelType(ProcuringEntity)
    lots = ListType(ModelType(ARMAPatchTenderLot, required=True), validators=[validate_uniq_id])

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class ARMATender(
    TenderSubmissionMixin, TenderGuaranteeMixin, TenderPeriodsMixin, TenderItemsMixin, TenderMilestonesMixin, BaseTender
):
    procurementMethodType = StringType(choices=[COMPLEX_ASSET_ARMA], required=True)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(ARMALot, required=True), validators=[validate_uniq_id])
