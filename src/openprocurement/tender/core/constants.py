from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from openprocurement.api.constants import ARTICLE_20, ARTICLE_21, TZ, ProcurementMethodType
from openprocurement.api.procedure.models.document import TenderDocumentType


class ReqStatuses(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    DEFAULT = ACTIVE


class TenderMilestoneType(StrEnum):
    FINANCING = "financing"
    DELIVERY = "delivery"


class ProcurementMethod(StrEnum):
    OPEN = "open"
    SELECTIVE = "selective"
    LIMITED = "limited"


SELECTIVE_PROCUREMENT_METHOD_TYPES = [
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
]

LAW_4888_PROCUREMENT_METHOD_TYPES_ENABLED = [
    ProcurementMethodType.OPEN_TENDERING,
]

LAW_4888_PROCUREMENT_METHOD_TYPES_DISABLED = []

BIDDER_TIME = timedelta(minutes=6)
SERVICE_TIME = timedelta(minutes=9)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)

CANT_DELETE_PERIOD_START_DATE_FROM = datetime(2016, 9, 23, tzinfo=TZ)
BID_LOTVALUES_VALIDATION_FROM = datetime(2016, 10, 21, tzinfo=TZ)

AMOUNT_NET_COEF = Decimal("1.2")

FIRST_STAGE_PROCUREMENT_TYPES = {
    ProcurementMethodType.BELOW_THRESHOLD,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    ProcurementMethodType.ESCO,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    ProcurementMethodType.REPORTING,
    ProcurementMethodType.NEGOTIATION,
    ProcurementMethodType.NEGOTIATION_QUICK,
    ProcurementMethodType.ABOVE_THRESHOLD_EU,
    ProcurementMethodType.ABOVE_THRESHOLD,
    ProcurementMethodType.ABOVE_THRESHOLD_UA,
    ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
    ProcurementMethodType.SIMPLE_DEFENSE,
    ProcurementMethodType.PRICE_QUOTATION,
    ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ProcurementMethodType.COMPETITIVE_ORDERING,
    ProcurementMethodType.OPEN_TENDERING,
}

CRITERION_TECHNICAL_FEATURES = "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"
CRITERION_LOCALIZATION = "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.LOCAL_ORIGIN_LEVEL"
CRITERION_SUBCONTRACTING_PROPORTION = (
    "CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.MANAGEMENT.SUBCONTRACTING_PROPORTION"
)
CRITERION_CONFLICT_OF_INTEREST_MISINTERPRETATION = "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION"
CRITERION_MISCONDUCT_MARKET_DISTORTION = "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION"

AWARD_ACTIVATION_BLOCKING_CRITERIA = {
    CRITERION_CONFLICT_OF_INTEREST_MISINTERPRETATION,
    CRITERION_MISCONDUCT_MARKET_DISTORTION,
}

ARTICLE_21_EXCLUDING_SUBCONTRACTING = ARTICLE_21 - {CRITERION_SUBCONTRACTING_PROPORTION}

SELECTION_CRITERIA_RULES = {
    "required_article_16": "article 16",
    "required_article_20": "article 20",
}

CRITERION_EVIDENCE_DOCUMENT_TYPES: dict[str, TenderDocumentType] = {
    **dict.fromkeys(ARTICLE_20, TenderDocumentType.EVALUATION_CRITERIA),
    **dict.fromkeys(ARTICLE_21_EXCLUDING_SUBCONTRACTING, TenderDocumentType.ELIGIBILITY_CRITERIA),
    CRITERION_SUBCONTRACTING_PROPORTION: TenderDocumentType.EVALUATION_CRITERIA,
}

EVIDENCE_DOCUMENT_CONTAINERS = (
    "documents",
    "financialDocuments",
    "eligibilityDocuments",
    "qualificationDocuments",
)

BID_EVIDENCE_DOCUMENT_RULES: dict[str, dict] = {
    **dict.fromkeys(
        ARTICLE_20,
        {
            "documentType": TenderDocumentType.QUALIFICATION_DOCUMENTS,
            "containers": ("documents",),
        },
    ),
    **dict.fromkeys(
        ARTICLE_21_EXCLUDING_SUBCONTRACTING,
        {
            "documentType": TenderDocumentType.ELIGIBILITY_DOCUMENTS,
            "containers": ("eligibilityDocuments",),
        },
    ),
    CRITERION_SUBCONTRACTING_PROPORTION: {
        "documentType": TenderDocumentType.QUALIFICATION_DOCUMENTS,
        "containers": ("qualificationDocuments",),
    },
}

PROCURING_ENTITY_EVIDENCE_DOCUMENT_RULES: dict[str, dict] = dict.fromkeys(
    ARTICLE_21_EXCLUDING_SUBCONTRACTING,
    {
        "documentType": TenderDocumentType.ELIGIBILITY_DOCUMENTS,
        "containers": ("documents",),
    },
)

COMPLAINT_AMOUNT_RATE = 0.3 / 100
COMPLAINT_MIN_AMOUNT = 2000
COMPLAINT_MAX_AMOUNT = 85000
COMPLAINT_ENHANCED_AMOUNT_RATE = 0.6 / 100
COMPLAINT_ENHANCED_MIN_AMOUNT = 3000
COMPLAINT_ENHANCED_MAX_AMOUNT = 170000


ALP_MILESTONE_REASONS = (
    "найбільш економічно вигідна пропозиція є меншою на 40 або більше відсотків від середньоарифметичного значення "
    "ціни/приведеної ціни тендерних пропозицій інших учасників",
    "найбільш економічно вигідна пропозиція є меншою на 30 або більше відсотків від наступної ціни/"
    "приведеної ціни тендерної пропозиції за результатами проведеного електронного аукціону",
)

ARMA_ALP_MILESTONE_REASONS = (
    "найбільш економічно вигідна пропозиція є меншою на 40 або більше відсотків від середньоарифметичного значення "
    "ціни/приведеної ціни тендерних пропозицій інших учасників на початковому етапі аукціону",
    ALP_MILESTONE_REASONS[1],
)


class AwardCriteria(StrEnum):
    LOWEST_COST = "lowestCost"
    LIFE_CYCLE_COST = "lifeCycleCost"
    RATED_CRITERIA = "ratedCriteria"


# Agreement errors
AGREEMENT_NOT_FOUND_MESSAGE = "Agreement not found"
AGREEMENT_STATUS_MESSAGE = "Agreement status is not active"
AGREEMENT_ITEMS_MESSAGE = "Agreement items is not subset of tender items"
AGREEMENT_START_DATE_MESSAGE = "agreements[0].period.startDate is > tender.date"
AGREEMENT_EXPIRED_MESSAGE = "Agreement ends less than {} days"
AGREEMENT_CHANGE_MESSAGE = "Agreement has pending change"
AGREEMENT_CONTRACTS_MESSAGE = "Agreement has less than {} active contracts"
AGREEMENT_IDENTIFIER_MESSAGE = (
    "tender.procuringEntity.identifier (scheme or id), "
    "doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)"
)
AGREEMENT_MILESTONES_MISMATCH_MESSAGE = "Agreement milestones does not match tender milestones"

CONTRACT_PERIOD_START_DAYS = 5

# which period calculations use working days (the open family value); calendar days everywhere otherwise
DEFAULT_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
CALENDAR_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}


AUCTION_SET_URLS_LOG_FIELDS = [
    "_id",
    "_rev",
    "status",
    "lots.id",
    "lots.status",
    "lots.auctionPeriod",
    "bids.id",
    "bids.status",
    "bids.date",
    "bids.lotValues.status",
    "bids.lotValues.relatedLot",
    "bids.lotValues.date",
    "bids.lotValues.participationUrl",
    "dateModified",
]

CHRONOGRAPH_PATCH_LOG_FIELDS = [
    "_id",
    "_rev",
    "status",
    "dateModified",
    "next_check",
]

# multilingual fields required by the EU-type procedures (openeu, esco, competitiveDialogue)
EU_REQUIRED_MULTILINGUAL_FIELDS = {
    "procuringEntity": {
        "name_en": True,
        "identifier": {"legalName_en": True},
        "contactPoint": {"name_en": True},
        "additionalContactPoints": {"name_en": True},
    },
    "items": {"description_en": True},
}
