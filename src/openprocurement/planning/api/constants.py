from datetime import timedelta
from enum import StrEnum
from itertools import chain

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.enums import enum_members

PROCEDURES = {
    "": ("", "centralizedProcurement"),
    "open": (
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
        ProcurementMethodType.ESCO,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
        ProcurementMethodType.OPEN_TENDERING,
    ),
    "selective": (
        ProcurementMethodType.PRICE_QUOTATION,
        ProcurementMethodType.COMPETITIVE_ORDERING,
    ),
    "limited": (
        ProcurementMethodType.REPORTING,
        ProcurementMethodType.NEGOTIATION,
        ProcurementMethodType.NEGOTIATION_QUICK,
    ),
}

MULTI_YEAR_BUDGET_PROCEDURES = (ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,)
MULTI_YEAR_BUDGET_MAX_YEARS = 4


CENTRAL_PROCUREMENT_IDENTIFIER_ID = "01101100"
CENTRAL_PROCUREMENT_APPROVE_TIME = timedelta(days=20)
PROCURING_ENTITY_STANDSTILL = timedelta(days=2)

MILESTONE_APPROVAL_DESCRIPTION = (
    "Узагальнення та аналіз отриманної інформації щодо проведення закупівель "
    "товарів, послуг (крім поточного ремонту) в інтересах замовників"
)


class BreakdownTitle(StrEnum):
    STATE = "state"
    CRIMEA = "crimea"
    LOCAL = "local"
    OWN = "own"
    FUND = "fund"
    LOAN = "loan"
    OTHER = "other"


PlanProcurementMethod = StrEnum("PlanProcurementMethod", enum_members(PROCEDURES))  # type: ignore[misc]
PlanProcurementMethodType = StrEnum(  # type: ignore[misc]
    "PlanProcurementMethodType", enum_members(chain(*PROCEDURES.values()))
)


class MilestoneType(StrEnum):
    APPROVAL = "approval"


class MilestoneStatus(StrEnum):
    SCHEDULED = "scheduled"
    MET = "met"
    NOT_MET = "notMet"
    INVALID = "invalid"


class MilestoneTitle(StrEnum):
    APPROVAL = "Підготовка до проведення процедури"


MILESTONE_ACTIVE_STATUSES = (MilestoneStatus.SCHEDULED, MilestoneStatus.MET)
