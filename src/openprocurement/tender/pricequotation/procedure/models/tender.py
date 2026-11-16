from pydantic import field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.constants_env import PQ_CRITERIA_ID_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.api.procedure.models.item import Classification
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.constants import AwardCriteria, ReqStatuses
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
from openprocurement.tender.pricequotation.constants import PriceQuotationProcurementMethodType
from openprocurement.tender.pricequotation.procedure.models.organization import PQShortlistedFirm


class PQPostTender(TenderSubmissionMixin, PostTenderItemsMixin, TenderMilestonesMixin, PostBaseTender):
    tenderPeriod: PeriodEndRequired
    awardPeriod: Period | None = None
    procurementMethodType: PriceQuotationProcurementMethodType = ProcurementMethodType.PRICE_QUOTATION
    awardCriteria: AwardCriteria | None = None
    agreement: AgreementUUID
    classification: Classification | None = None
    value: Value
    procuringEntity: ProcuringEntity
    criteria: list[Criterion] | None = None

    @model_field_validator("awardPeriod")
    def validate_award_period(self, period):
        validate_award_period(self, period)

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_pq_criteria_id_uniq(value)
        return value


class PQPatchTender(TenderSubmissionMixin, PatchTenderItemsMixin, PatchTenderMilestonesMixin, PatchBaseTender):
    enquiryPeriod: PeriodEndRequired | None = None
    tenderPeriod: PeriodEndRequired | None = None
    awardPeriod: Period | None = None
    awardCriteria: AwardCriteria | None = None
    profile: str | None = None
    agreement: AgreementUUID | None = None
    value: Value | None = None
    procuringEntity: ProcuringEntity | None = None
    classification: Classification | None = None
    criteria: list[Criterion] | None = None

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_pq_criteria_id_uniq(value)
        return value


class PQTender(TenderSubmissionMixin, TenderItemsMixin, TenderMilestonesMixin, BaseTender):
    tenderPeriod: PeriodEndRequired | None = None
    awardPeriod: Period | None = None
    procurementMethodType: PriceQuotationProcurementMethodType
    awardCriteria: AwardCriteria
    profile: str | None = None
    agreement: AgreementUUID
    shortlistedFirms: list[PQShortlistedFirm] | None = None
    value: Value
    procuringEntity: ProcuringEntity
    classification: Classification | None = None
    unsuccessfulReason: list[str] | None = None
    criteria: list[Criterion] | None = None

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_pq_criteria_id_uniq(value)
        return value


def validate_pq_criteria_id_uniq(objs, *args):
    if not objs:
        return
    tender = get_tender()
    if get_first_revision_date(tender, default=get_request_now()) > PQ_CRITERIA_ID_FROM:
        ids = [i.id for i in objs]
        if len(set(ids)) != len(ids):
            raise ValidationError("Criteria id should be uniq")

        rg_ids = [rg.id for c in objs for rg in c.requirementGroups or ""]
        if len(rg_ids) != len(set(rg_ids)):
            raise ValidationError("Requirement group id should be uniq in tender")

        req_ids = [req.id for c in objs for rg in c.requirementGroups or "" for req in rg.requirements or ""]
        if len(req_ids) != len(set(req_ids)):
            raise ValidationError("Requirement id should be uniq for all requirements in tender")

        for criterion in objs:
            for rg in criterion.requirementGroups or "":
                req_titles = [req.title for req in rg.requirements or "" if req.status == ReqStatuses.ACTIVE]
                if len(set(req_titles)) != len(req_titles):
                    raise ValidationError("Requirement title should be uniq for one requirementGroup")
