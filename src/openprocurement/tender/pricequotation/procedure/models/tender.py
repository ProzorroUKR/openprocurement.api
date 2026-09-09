from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.item import Classification
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.constants import AWARD_CRITERIA_CHOICES
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.criterion import Criterion
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderSubmissionMixin,
    validate_award_period,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender
from openprocurement.tender.core.procedure.validation import validate_pq_criteria_id_uniq
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.models.organization import PQShortlistedFirm


class PQPostTender(TenderSubmissionMixin, PostTenderItemsMixin, TenderMilestonesMixin, PostBaseTender):
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    procurementMethodType = StringType(choices=[PQ], default=PQ)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    agreement = ModelType(AgreementUUID, required=True)
    classification = ModelType(Classification)

    value = ModelType(Value, required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_pq_criteria_id_uniq],
    )

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)


class PQPatchTender(TenderSubmissionMixin, PatchTenderItemsMixin, PatchTenderMilestonesMixin, PatchBaseTender):
    enquiryPeriod = ModelType(PeriodEndRequired)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    profile = StringType()
    agreement = ModelType(AgreementUUID)

    value = ModelType(Value)
    procuringEntity = ModelType(ProcuringEntity)

    classification = ModelType(Classification)

    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_pq_criteria_id_uniq],
    )


class PQTender(TenderSubmissionMixin, TenderItemsMixin, TenderMilestonesMixin, BaseTender):
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    procurementMethodType = StringType(choices=[PQ], required=True)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES, required=True)
    profile = StringType()
    agreement = ModelType(AgreementUUID, required=True)
    shortlistedFirms = ListType(ModelType(PQShortlistedFirm))

    value = ModelType(Value, required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    classification = ModelType(Classification)
    unsuccessfulReason = ListType(StringType)  # deprecated after PQ bot removing

    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_pq_criteria_id_uniq],
    )
