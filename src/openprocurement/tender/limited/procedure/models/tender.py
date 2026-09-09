from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.core.procedure.models.criterion import Criterion, validate_criteria_requirement_uniq
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    validate_negotiation_cause,
    validate_negotiation_quick_cause,
    validate_reporting_cause,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, CommonBaseTender, PostBaseTender
from openprocurement.tender.core.procedure.validation import validate_funders_ids, validate_object_id_uniq
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.limited.procedure.models.lot import LimitedLot, LimitedPatchTenderLot, LimitedPostTenderLot
from openprocurement.tender.limited.procedure.models.organization import ReportingFundOrganization
from openprocurement.tender.limited.procedure.models.tender_base import LimitedCauseDetails


class ReportingPostTender(PostTenderItemsMixin, TenderMilestonesMixin, PostBaseTender):
    _items_related_lot_check = False

    procurementMethodType = StringType(choices=[REPORTING], default=REPORTING)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(Value)

    funders = ListType(
        ModelType(ReportingFundOrganization, required=True),
        validators=[validate_funders_ids],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_cause(self, data, value):
        validate_reporting_cause(value)


class ReportingPatchTender(PatchTenderItemsMixin, PatchTenderMilestonesMixin, CommonBaseTender):
    procurementMethodType = StringType(choices=[REPORTING])
    procuringEntity = ModelType(ProcuringEntity)
    value = ModelType(Value)

    funders = ListType(
        ModelType(ReportingFundOrganization, required=True),
        validators=[validate_funders_ids],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )


class ReportingTender(TenderItemsMixin, TenderMilestonesMixin, BaseTender):
    _items_related_lot_check = False

    procurementMethodType = StringType(choices=[REPORTING], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(Value)

    funders = ListType(
        ModelType(ReportingFundOrganization, required=True),
        validators=[validate_funders_ids],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_cause(self, data, value):
        validate_reporting_cause(value)


class NegotiationPostTender(PostTenderItemsMixin, TenderMilestonesMixin, PostBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], default=NEGOTIATION)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(Value, required=True)
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    lots = ListType(ModelType(LimitedPostTenderLot, required=True), validators=[validate_uniq_id])

    def validate_cause(self, data, value):
        validate_negotiation_cause(value)


class NegotiationPatchTender(PatchTenderItemsMixin, PatchTenderMilestonesMixin, CommonBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION])
    procuringEntity = ModelType(ProcuringEntity)
    value = ModelType(Value)
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    lots = ListType(ModelType(LimitedPatchTenderLot, required=True), validators=[validate_uniq_id])

    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )


class NegotiationTender(TenderItemsMixin, TenderMilestonesMixin, BaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(Value, required=True)
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    lots = ListType(ModelType(LimitedLot, required=True), validators=[validate_uniq_id])

    def validate_cause(self, data, value):
        validate_negotiation_cause(value)


class NegotiationQuickPostTender(NegotiationPostTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK], default=NEGOTIATION_QUICK)
    cause = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_cause(self, data, value):
        validate_negotiation_quick_cause(value)


class NegotiationQuickPatchTender(NegotiationPatchTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK])
    causeDetails = ModelType(LimitedCauseDetails)


class NegotiationQuickTender(NegotiationTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK], required=True)
    cause = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_cause(self, data, value):
        validate_negotiation_quick_cause(value)
