from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.cfaselectionua.procedure.models.agreement import CFASelectionAgreement
from openprocurement.tender.cfaselectionua.procedure.models.feature import CFASelectionFeature
from openprocurement.tender.cfaselectionua.procedure.models.lot import (
    CFASelectionLot,
    CFASelectionPatchTenderLot,
    CFASelectionPostTenderLot,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_CHOICES
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderSubmissionMixin,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender
from openprocurement.tender.core.procedure.models.value import BasicValue


class CFASelectionPostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    procurementMethodType = StringType(choices=[CFA_SELECTION], default=CFA_SELECTION)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    agreements = ListType(ModelType(AgreementUUID, required=True), required=True, min_size=1, max_size=1)
    lots = ListType(
        ModelType(CFASelectionPostTenderLot, required=True),
        min_size=1,
        max_size=1,
        required=True,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])


class CFASelectionPatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    procurementMethodType = StringType(choices=[CFA_SELECTION])
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procuringEntity = ModelType(ProcuringEntity)

    lots = ListType(
        ModelType(CFASelectionPatchTenderLot, required=True),
        min_size=1,
        max_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)

    tenderPeriod = ModelType(PeriodEndRequired)
    # will be overwritten by serializable
    minimalStep = ModelType(Value)

    def validate_tenderPeriod(self, data, period):
        if period and get_tender()["status"] != "active.enquiries":
            raise ValidationError("Rogue field")


class CFASelectionTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    BaseTender,
):
    procurementMethodType = StringType(choices=[CFA_SELECTION], required=True)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES, required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    agreements = ListType(ModelType(CFASelectionAgreement, required=True), required=True, min_size=1, max_size=1)
    lots = ListType(
        ModelType(CFASelectionLot, required=True),
        min_size=1,
        max_size=1,
        required=True,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    tenderPeriod = ModelType(PeriodEndRequired)
    enquiryPeriod = ModelType(PeriodEndRequired)
    # will be overwritten by serializable
    minimalStep = ModelType(Value)
    value = ModelType(Value)

    # Non-required mainProcurementCategory
    # Not required milestones
    @serializable(
        serialized_name="guarantee",
        serialize_when_none=False,
        type=ModelType(BasicValue),
    )
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {"amount": sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee["currency"] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee["currency"] = self.guarantee.currency
            guarantee_class = self._fields["guarantee"]
            return guarantee_class(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStep", type=ModelType(Value, required=False))
    def tender_minimalStep(self):
        return self.minimalStep

    @serializable(serialized_name="value", type=ModelType(Value))
    def tender_value(self):
        return self.value
