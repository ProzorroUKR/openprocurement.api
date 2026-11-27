import os
import re
from collections import ChainMap
from datetime import time
from enum import StrEnum
from logging import getLogger

import standards
from pytz import timezone
from requests import Session

from openprocurement.api import constants_env
from openprocurement.api.constants_utils import (
    filter_archeved_items,
    load_criteria_rules,
    load_rationale_types,
    parse_str_list,
    split_classifier_by_year,
)
from openprocurement.api.enums import enum_members


class ProcurementMethodType(StrEnum):
    """procurementMethodType of the tenders"""

    BELOW_THRESHOLD = "belowThreshold"
    ABOVE_THRESHOLD = "aboveThreshold"
    ABOVE_THRESHOLD_UA = "aboveThresholdUA"
    ABOVE_THRESHOLD_EU = "aboveThresholdEU"
    ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"
    SIMPLE_DEFENSE = "simple.defense"
    COMPETITIVE_ORDERING = "competitiveOrdering"
    REQUEST_FOR_PROPOSAL = "requestForProposal"
    OPEN_TENDERING = "openTendering"
    COMPETITIVE_DIALOGUE_UA = "competitiveDialogueUA"
    COMPETITIVE_DIALOGUE_EU = "competitiveDialogueEU"
    COMPETITIVE_DIALOGUE_UA_STAGE2 = "competitiveDialogueUA.stage2"
    COMPETITIVE_DIALOGUE_EU_STAGE2 = "competitiveDialogueEU.stage2"
    ESCO = "esco"
    CLOSE_FRAMEWORK_AGREEMENT_UA = "closeFrameworkAgreementUA"
    CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA = "closeFrameworkAgreementSelectionUA"
    REPORTING = "reporting"
    NEGOTIATION = "negotiation"
    NEGOTIATION_QUICK = "negotiation.quick"
    PRICE_QUOTATION = "priceQuotation"
    COMPLEX_ASSET_ARMA = "complexAsset.arma"
    SIMPLE_ASSET_ARMA = "simpleAsset.arma"


class FrameworkType(StrEnum):
    """frameworkType of the frameworks (submissionType and qualificationType as well)"""

    ELECTRONIC_CATALOGUE = "electronicCatalogue"
    DYNAMIC_PURCHASING_SYSTEM = "dynamicPurchasingSystem"
    INTERNATIONAL_FINANCIAL_INSTITUTIONS = "internationalFinancialInstitutions"
    ASSET_RECOVERY_MANAGEMENT_AGENCY = "assetRecoveryManagementAgency"


class AgreementType(StrEnum):
    """agreementType of the agreements: of the frameworks and of closeFrameworkAgreementUA tenders"""

    ELECTRONIC_CATALOGUE = FrameworkType.ELECTRONIC_CATALOGUE.value
    DYNAMIC_PURCHASING_SYSTEM = FrameworkType.DYNAMIC_PURCHASING_SYSTEM.value
    INTERNATIONAL_FINANCIAL_INSTITUTIONS = FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS.value
    ASSET_RECOVERY_MANAGEMENT_AGENCY = FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY.value
    CLOSE_FRAMEWORK_AGREEMENT_UA = ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA.value


# Logging
LOGGER = getLogger("openprocurement.api")

# Api route
VERSION = "2.5"
ROUTE_PREFIX = "/api/{}".format(VERSION)

# Session
SESSION = Session()

# OCDS
OCID_PREFIX = os.environ.get("OCID_PREFIX", "ocds-be6bcu")

# Timezone
TZ = timezone(os.environ["TZ"] if "TZ" in os.environ else "Europe/Kiev")

# Sandbox mode
SANDBOX_MODE = os.environ.get("SANDBOX_MODE", False)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Tenders in which could be used criteria connected with guarantee
GUARANTEE_ALLOWED_TENDER_TYPES = (
    ProcurementMethodType.BELOW_THRESHOLD,
    ProcurementMethodType.ABOVE_THRESHOLD,
    ProcurementMethodType.COMPETITIVE_ORDERING,
    ProcurementMethodType.ABOVE_THRESHOLD_UA,
    ProcurementMethodType.ABOVE_THRESHOLD_EU,
    ProcurementMethodType.ESCO,
    ProcurementMethodType.PRICE_QUOTATION,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ProcurementMethodType.OPEN_TENDERING,
)

CONTRACT_GUARANTEE_ALLOWED_TENDER_TYPES = (
    ProcurementMethodType.BELOW_THRESHOLD,
    ProcurementMethodType.ABOVE_THRESHOLD,
    ProcurementMethodType.COMPETITIVE_ORDERING,
    ProcurementMethodType.ABOVE_THRESHOLD_UA,
    ProcurementMethodType.ABOVE_THRESHOLD_EU,
    ProcurementMethodType.ESCO,
    ProcurementMethodType.PRICE_QUOTATION,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ProcurementMethodType.SIMPLE_DEFENSE,
    ProcurementMethodType.OPEN_TENDERING,
)

BID_GUARANTEE_ALLOWED_TENDER_TYPES = (
    ProcurementMethodType.BELOW_THRESHOLD,
    ProcurementMethodType.ABOVE_THRESHOLD,
    ProcurementMethodType.COMPETITIVE_ORDERING,
    ProcurementMethodType.ABOVE_THRESHOLD_UA,
    ProcurementMethodType.ABOVE_THRESHOLD_EU,
    ProcurementMethodType.ESCO,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ProcurementMethodType.SIMPLE_DEFENSE,
    ProcurementMethodType.OPEN_TENDERING,
)

BID_REQUIRED_ITEMS_TENDER_TYPES = (
    ProcurementMethodType.BELOW_THRESHOLD,
    ProcurementMethodType.ABOVE_THRESHOLD,
    ProcurementMethodType.COMPETITIVE_ORDERING,
    ProcurementMethodType.ABOVE_THRESHOLD_UA,
    ProcurementMethodType.ABOVE_THRESHOLD_EU,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    ProcurementMethodType.ESCO,
    ProcurementMethodType.PRICE_QUOTATION,
    ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ProcurementMethodType.OPEN_TENDERING,
)

# Calendar
WORKING_DAYS = {}
HOLIDAYS = standards.load("calendars/workdays_off.json")
for date_str in HOLIDAYS:
    WORKING_DAYS[date_str] = True
# the defense procedures also treat the "weekends on" days as working days
WORKING_DAYS_WITH_WORKING_WEEKENDS = dict(WORKING_DAYS)
for date_str in standards.load("calendars/weekends_on.json"):
    WORKING_DAYS_WITH_WORKING_WEEKENDS[date_str] = False

# Deprecated user agents
DEPRECATED_FEED_USER_AGENTS = parse_str_list(os.environ.get("DEPRECATED_FEED_USER_AGENTS", ""))

# Time offset for tenderPeriod.startDate that allows to activate tender
TENDER_PERIOD_START_DATE_STALE_MINUTES = int(os.environ.get("TENDER_PERIOD_START_DATE_STALE_MINUTES", 10))

# CPV and DK021
CPV_PHARM_PRODUCTS = "33600000-6"
CPV_NOT_CPV = "99999999-9"

CPV_CODES = list(standards.load("classifiers/cpv_en.json"))
CPV_CODES.append(CPV_NOT_CPV)
DK_CODES = list(standards.load("classifiers/dk021_uk.json"))

CPV_GROUP_PREFIX_LENGTH = 3
CPV_CLASS_PREFIX_LENGTH = 4

CPV_DEFAULT_PREFIX_LENGTH = CPV_CLASS_PREFIX_LENGTH
CPV_PHARM_PREFIX_LENGTH = CPV_GROUP_PREFIX_LENGTH

CPV_PHARM_PREFIX = CPV_PHARM_PRODUCTS[:CPV_PHARM_PREFIX_LENGTH]

CPV_PREFIX_LENGTH_TO_NAME = {
    CPV_GROUP_PREFIX_LENGTH: "group",
    CPV_CLASS_PREFIX_LENGTH: "class",
}

# Funders
FUNDERS = {
    (i["identifier"]["scheme"], i["identifier"]["id"]): i for i in standards.load("codelists/tender/tender_funder.json")
}

# Codes
ORA_CODES = [i["code"] for i in standards.load("organizations/identifier_scheme.json")["data"]]

# Classifiers
# (extended keys gmdn contains actual and obsolete codes, since deleted codes can block un-refactored endpoints)
GMDN_2019 = set(standards.load("classifiers/gmdn.json"))
GMDN_2023 = set(standards.load("classifiers/gmdn_2023.json"))
GMDN_CPV_PREFIXES = standards.load("classifiers/gmdn_cpv_prefixes.json")
UA_ROAD = standards.load("classifiers/ua_road.json")
UA_ROAD_CPV_PREFIXES = standards.load("classifiers/ua_road_cpv_prefixes.json")
CCCE_UA = standards.load("classifiers/ccce_ua.json")
KPKV_UK = standards.load("classifiers/kpkv_uk_2025.json")
KEKV_UK = standards.load("classifiers/kekv_uk.json")
KPK = split_classifier_by_year(standards.load("classifiers/kpk.json"), "КПК")
KATOTTG = standards.load("classifiers/katottg.json")
TKPKMB = standards.load("classifiers/tkpkmb.json")
UKTZED = set(standards.load("classifiers/uktzed.json"))

# Complaint objections classifications
ARTICLE_16 = {criterion["classification"]["id"] for criterion in standards.load("criteria/article_16.json")}
ARTICLE_17 = {criterion["classification"]["id"] for criterion in standards.load("criteria/article_17.json")}
ARTICLE_20 = {
    criterion["classification"]["id"]
    for criterion in standards.load("criteria/law_4888/tender/selection_criteria.json")
}
ARTICLE_21 = {
    criterion["classification"]["id"]
    for criterion in standards.load("criteria/law_4888/tender/exclusion_criteria.json")
}
OTHER_CRITERIA = {criterion["classification"]["id"] for criterion in standards.load("criteria/other.json")}

# additional criteria
CRITERION_LIFE_CYCLE_COST_IDS = {criterion["classification"]["id"] for criterion in standards.load("criteria/LCC.json")}
DECREE_1178 = {criterion["classification"]["id"] for criterion in standards.load("criteria/decree_1178.json")}
CRITERIA_UKRAINE_FACILITY = {
    criterion["classification"]["id"] for criterion in standards.load("criteria/ukraine_facility.json")
}
DECREE_822 = {criterion["classification"]["id"] for criterion in standards.load("criteria/decree_822.json")}

CRITERIA_LIST = (
    ARTICLE_16
    | ARTICLE_17
    | ARTICLE_21
    | OTHER_CRITERIA
    | CRITERION_LIFE_CYCLE_COST_IDS
    | DECREE_1178
    | CRITERIA_UKRAINE_FACILITY
    | DECREE_822
)

# AMCU
VIOLATION_AMCU = set(standards.load("AMCU/violation_amcu.json"))
AMCU = set(standards.load("AMCU/amcu.json"))
AMCU_24 = set(standards.load("AMCU/amcu_24.json"))
REQUESTED_REMEDIES_TYPES = set(standards.load("AMCU/requested_remedies_type.json"))

# Schemes
INN_SCHEME = "INN"
ATC_SCHEME = "ATC"
GMDN_2019_SCHEME = "GMDN"
GMDN_2023_SCHEME = "GMDN-2023"
UA_ROAD_SCHEME = "UA-ROAD"
CCCE_UA_SCHEME = "CCCE-UA"
KPKV_UK_SCHEME = "КПКВ"
KEKV_UK_SCHEME = "КЕКВ"
KPK_SCHEME = "КПК"
KPK_SCHEMES = KPK.keys()
KATOTTG_SCHEME = "КАТОТТГ"
TKPKMB_SCHEME = "ТПКВКМБ"
UKTZED_SCHEME = "UKTZED"

# Additional schemes
ADDITIONAL_CLASSIFICATIONS_SCHEMES = [
    "ДК003",
    "ДК015",
    "ДК018",
    "specialNorms",
]

# Coordinates regex
COORDINATES_REG_EXP = re.compile(r"-?\d{1,3}\.\d+|-?\d{1,3}")

# Tender config
TENDER_CONFIG_JSONSCHEMAS = {
    ProcurementMethodType.ABOVE_THRESHOLD: standards.load("data_model/schema/TenderConfig/aboveThreshold.json"),
    ProcurementMethodType.COMPETITIVE_ORDERING: standards.load(
        "data_model/schema/TenderConfig/competitiveOrdering.json"
    ),
    ProcurementMethodType.ABOVE_THRESHOLD_EU: standards.load("data_model/schema/TenderConfig/aboveThresholdEU.json"),
    ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: standards.load(
        "data_model/schema/TenderConfig/aboveThresholdUA.defense.json"
    ),
    ProcurementMethodType.ABOVE_THRESHOLD_UA: standards.load("data_model/schema/TenderConfig/aboveThresholdUA.json"),
    ProcurementMethodType.BELOW_THRESHOLD: standards.load("data_model/schema/TenderConfig/belowThreshold.json"),
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA: standards.load(
        "data_model/schema/TenderConfig/closeFrameworkAgreementSelectionUA.json"
    ),
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA: standards.load(
        "data_model/schema/TenderConfig/closeFrameworkAgreementUA.json"
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU: standards.load(
        "data_model/schema/TenderConfig/competitiveDialogueEU.json"
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2: standards.load(
        "data_model/schema/TenderConfig/competitiveDialogueEU.stage2.json"
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA: standards.load(
        "data_model/schema/TenderConfig/competitiveDialogueUA.json"
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2: standards.load(
        "data_model/schema/TenderConfig/competitiveDialogueUA.stage2.json"
    ),
    ProcurementMethodType.ESCO: standards.load("data_model/schema/TenderConfig/esco.json"),
    ProcurementMethodType.NEGOTIATION: standards.load("data_model/schema/TenderConfig/negotiation.json"),
    ProcurementMethodType.NEGOTIATION_QUICK: standards.load("data_model/schema/TenderConfig/negotiation.quick.json"),
    ProcurementMethodType.PRICE_QUOTATION: standards.load("data_model/schema/TenderConfig/priceQuotation.json"),
    ProcurementMethodType.REPORTING: standards.load("data_model/schema/TenderConfig/reporting.json"),
    ProcurementMethodType.SIMPLE_DEFENSE: standards.load("data_model/schema/TenderConfig/simple.defense.json"),
    ProcurementMethodType.REQUEST_FOR_PROPOSAL: standards.load(
        "data_model/schema/TenderConfig/requestForProposal.json"
    ),
    ProcurementMethodType.COMPLEX_ASSET_ARMA: standards.load("data_model/schema/TenderConfig/complexAsset.arma.json"),
    ProcurementMethodType.SIMPLE_ASSET_ARMA: standards.load("data_model/schema/TenderConfig/simpleAsset.arma.json"),
    ProcurementMethodType.OPEN_TENDERING: standards.load("data_model/schema/TenderConfig/openTendering.json"),
}

TENDER_CO_CONFIG_JSONSCHEMAS = {
    "competitiveOrdering.long": standards.load("data_model/schema/TenderConfig/competitiveOrdering.long.json"),
    "competitiveOrdering.short": standards.load("data_model/schema/TenderConfig/competitiveOrdering.short.json"),
}

# openTendering: the UA/EU variant config schemas (selected by the tender field procedure.euPublished)
TENDER_OPEN_TENDERING_CONFIG_JSONSCHEMAS = {
    "openTendering.UA": standards.load("data_model/schema/TenderConfig/openTendering.UA.json"),
    "openTendering.EU": standards.load("data_model/schema/TenderConfig/openTendering.EU.json"),
}

# the additional config schemas validated on top of the procedure schema (competitiveOrdering, openTendering)
# (a ChainMap: the tests replace the schemas of the dicts above in place)
TENDER_EXTRA_CONFIG_JSONSCHEMAS = ChainMap(TENDER_CO_CONFIG_JSONSCHEMAS, TENDER_OPEN_TENDERING_CONFIG_JSONSCHEMAS)

# the schemas of the tender field procedure: the procedure specific fields (procedureExtensionScheme)
TENDER_PROCEDURE_JSONSCHEMAS = {
    procurement_method_type: description["procedureExtensionScheme"]
    for procurement_method_type, description in standards.load(
        "codelists/tender/tender_procurement_method_type.json"
    ).items()
    if "procedureExtensionScheme" in description
}

# Framework config
FRAMEWORK_CONFIG_JSONSCHEMAS = {
    FrameworkType.ELECTRONIC_CATALOGUE: standards.load("data_model/schema/FrameworkConfig/electronicCatalogue.json"),
    FrameworkType.DYNAMIC_PURCHASING_SYSTEM: standards.load(
        "data_model/schema/FrameworkConfig/dynamicPurchasingSystem.json"
    ),
    FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS: standards.load(
        "data_model/schema/FrameworkConfig/internationalFinancialInstitutions.json"
    ),
    FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY: standards.load(
        "data_model/schema/FrameworkConfig/assetRecoveryManagementAgency.json"
    ),
}

# Framework period change causes
PERIOD_CHANGE_CAUSES = {
    cause: desc["title_uk"]
    for cause, desc in standards.load("codelists/frameworks/framework_period_change_causes.json").items()
}

# Journal prefix
JOURNAL_PREFIX = os.environ.get("JOURNAL_PREFIX", "JOURNAL_")

# CS-11442 contract/items/additionalClassifications scheme: COO
COUNTRIES_MAP = standards.load("classifiers/countries.json")

# Address validation
COUNTRIES = {c["name_uk"] for c in COUNTRIES_MAP.values()}
UA_REGIONS = standards.load("classifiers/ua_regions.json")

# CS-10431 validation currency
CURRENCIES = standards.load("codelists/tender/tender_currency.json")

# Decided in CS-8167
MINIMAL_STEP_VALIDATION_PRESCISSION = 2
MINIMAL_STEP_VALIDATION_LOWER_LIMIT = 0.005
MINIMAL_STEP_VALIDATION_UPPER_LIMIT = 0.03

# Contract templates
CONTRACT_TEMPLATES = standards.load("templates/contract_templates.json")
DEFAULT_CONTRACT_TEMPLATE_KEY = "general"

# milestone dictionaries
MILESTONE_CODES = {
    "delivery": {
        key for key, desc in standards.load("codelists/milestones/code.json").items() if "delivery" in desc["type"]
    },
    "financing": {
        key for key, desc in standards.load("codelists/milestones/code.json").items() if "financing" in desc["type"]
    },
}
MILESTONE_TITLES = {
    "delivery": {
        key for key, desc in standards.load("codelists/milestones/title.json").items() if "delivery" in desc["type"]
    },
    "financing": {
        key for key, desc in standards.load("codelists/milestones/title.json").items() if "financing" in desc["type"]
    },
}
MILESTONE_ACTIVE_DURATION_TYPES = ("working", "calendar")
MILESTONE_ARCHIVED_DURATION_TYPES = ("banking",)
MILESTONE_DURATION_TYPES = MILESTONE_ACTIVE_DURATION_TYPES + MILESTONE_ARCHIVED_DURATION_TYPES

# cause for reporting
TENDER_CAUSE = {
    key for key, desc in standards.load("codelists/tender/tender_cause.json").items() if desc["archive"] is False
}

TENDER_CAUSE_REPORTING_ALL = standards.load("codelists/tender/tender_cause_details/reporting.json")
TENDER_CAUSE_REPORTING = filter_archeved_items(TENDER_CAUSE_REPORTING_ALL)

TENDER_CAUSE_NEGOTIATION_ALL = standards.load("codelists/tender/tender_cause_details/negotiation.json")
TENDER_CAUSE_NEGOTIATION = filter_archeved_items(TENDER_CAUSE_NEGOTIATION_ALL)

TENDER_CAUSE_NEGOTIATION_QUICK_ALL = standards.load("codelists/tender/tender_cause_details/negotiation.quick.json")
TENDER_CAUSE_NEGOTIATION_QUICK = filter_archeved_items(TENDER_CAUSE_NEGOTIATION_QUICK_ALL)

# only active causes
PROCUREMENT_METHOD_TYPE_TO_CAUSE_DETAILS_MAPPING = {
    ProcurementMethodType.REPORTING: TENDER_CAUSE_REPORTING,
    ProcurementMethodType.NEGOTIATION: TENDER_CAUSE_NEGOTIATION,
    ProcurementMethodType.NEGOTIATION_QUICK: TENDER_CAUSE_NEGOTIATION_QUICK,
}

PROCUREMENT_METHOD_TYPE_TO_CAUSE_DETAILS_MAPPING_ALL = {
    ProcurementMethodType.REPORTING: TENDER_CAUSE_REPORTING_ALL,
    ProcurementMethodType.NEGOTIATION: TENDER_CAUSE_NEGOTIATION_ALL,
    ProcurementMethodType.NEGOTIATION_QUICK: TENDER_CAUSE_NEGOTIATION_QUICK_ALL,
}

# Should be at the end of the file for now
# TODO: move to modules initialization
TENDER_CRITERIA_RULES = {
    ProcurementMethodType.ABOVE_THRESHOLD: load_criteria_rules(ProcurementMethodType.ABOVE_THRESHOLD, constants_env),
    ProcurementMethodType.COMPETITIVE_ORDERING: load_criteria_rules(
        ProcurementMethodType.COMPETITIVE_ORDERING, constants_env
    ),
    ProcurementMethodType.ABOVE_THRESHOLD_EU: load_criteria_rules(
        ProcurementMethodType.ABOVE_THRESHOLD_EU, constants_env
    ),
    ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: load_criteria_rules(
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE, constants_env
    ),
    ProcurementMethodType.ABOVE_THRESHOLD_UA: load_criteria_rules(
        ProcurementMethodType.ABOVE_THRESHOLD_UA, constants_env
    ),
    ProcurementMethodType.BELOW_THRESHOLD: load_criteria_rules(ProcurementMethodType.BELOW_THRESHOLD, constants_env),
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA: load_criteria_rules(
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA, constants_env
    ),
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA: load_criteria_rules(
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA, constants_env
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU: load_criteria_rules(
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU, constants_env
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2: load_criteria_rules(
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2, constants_env
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA: load_criteria_rules(
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA, constants_env
    ),
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2: load_criteria_rules(
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2, constants_env
    ),
    ProcurementMethodType.ESCO: load_criteria_rules(ProcurementMethodType.ESCO, constants_env),
    ProcurementMethodType.NEGOTIATION: load_criteria_rules(ProcurementMethodType.NEGOTIATION, constants_env),
    ProcurementMethodType.NEGOTIATION_QUICK: load_criteria_rules(
        ProcurementMethodType.NEGOTIATION_QUICK, constants_env
    ),
    ProcurementMethodType.PRICE_QUOTATION: load_criteria_rules(ProcurementMethodType.PRICE_QUOTATION, constants_env),
    ProcurementMethodType.REPORTING: load_criteria_rules(ProcurementMethodType.REPORTING, constants_env),
    ProcurementMethodType.SIMPLE_DEFENSE: load_criteria_rules(ProcurementMethodType.SIMPLE_DEFENSE, constants_env),
    ProcurementMethodType.COMPLEX_ASSET_ARMA: load_criteria_rules(
        ProcurementMethodType.COMPLEX_ASSET_ARMA, constants_env
    ),
    ProcurementMethodType.SIMPLE_ASSET_ARMA: load_criteria_rules(
        ProcurementMethodType.SIMPLE_ASSET_ARMA, constants_env
    ),
    ProcurementMethodType.OPEN_TENDERING: load_criteria_rules(ProcurementMethodType.OPEN_TENDERING, constants_env),
}

# Auction plannning configuration
AUCTION_DAY_START = time(11, 0)
AUCTION_DAY_END = time(16, 0)
HALF_HOUR_SECONDS = 30 * 60

AUCTION_PERIOD_SHOULD_START_EARLIER_UPDATE_DAYS = int(
    os.environ.get("AUCTION_PERIOD_SHOULD_START_EARLIER_UPDATE_DAYS", 2)
)

AUCTION_REPLAN_BUFFER_MINUTES = int(os.environ.get("AUCTION_REPLAN_BUFFER_MINUTES", 60))

# simplified way to get nuber of half-hours fit in period
# (it does not include minutes)
AUCTION_TIME_SLOTS_NUMBER = (AUCTION_DAY_END.hour - AUCTION_DAY_START.hour) * 2

# Plan of Ukraine
PLAN_OF_UKRAINE = standards.load("classifiers/plan_of_ukraine.json")

# CS-21350 Donor programs
PLAN_OF_UKRAINE_SCHEME = "plan_of_ukraine"
FUNDER_PROGRAM_SCHEME = "funder_program"
FUNDER_PROGRAMS = {item["id"]: item for item in standards.load("codelists/plans/funder_program.json")}

# Language codes
LANGUAGE_CODES = standards.load("classifiers/languages.json").keys()

# CS-19019
PROFILE_REQUIRED_MIN_VALUE_AMOUNT = 500000

# CS-19545
BROKERS = {broker["name"]: broker["title"] for broker in standards.load("organizations/brokers.json")}

KIND_PROCUREMENT_METHOD_TYPE_MAPPING = standards.load("organizations/kind_procurementMethodType_mapping.json")
KIND_FRAMEWORK_TYPE_MAPPING = standards.load("organizations/kind_frameworkType_mapping.json")

RATIONALE_TYPES_DECREE_1178_ALL = load_rationale_types("codelists/contract_change_rationale_type_decree_1178.json")
RATIONALE_TYPES_DECREE_1178 = filter_archeved_items(RATIONALE_TYPES_DECREE_1178_ALL)

RATIONALE_TYPES_LAW_922_ALL = load_rationale_types("codelists/contract_change_rationale_type_law_922.json")
RATIONALE_TYPES_LAW_922 = filter_archeved_items(RATIONALE_TYPES_LAW_922_ALL)

CAUSE_TO_RATIONALE_TYPES_MAPPING = {
    "LAW922": RATIONALE_TYPES_LAW_922,
    "DECREE1178": RATIONALE_TYPES_DECREE_1178,
    "DECREE1275": RATIONALE_TYPES_DECREE_1178,
}

CAUSE_TO_RATIONALE_TYPES_MAPPING_ALL = {
    "LAW922": RATIONALE_TYPES_LAW_922_ALL,
    "DECREE1178": RATIONALE_TYPES_DECREE_1178_ALL,
    "DECREE1275": RATIONALE_TYPES_DECREE_1178_ALL,
}

TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178 = (
    ProcurementMethodType.ABOVE_THRESHOLD,
    ProcurementMethodType.PRICE_QUOTATION,
)

# profile id of the market catalogue (items of plans, tenders)
PQ_PROFILE_PATTERN = re.compile(r"^\d{6}-\d{8}-\d{6}-\d{8}")


# enums of the values above (for the models)
OraCode = StrEnum("OraCode", enum_members(ORA_CODES))  # type: ignore[misc]
PeriodChangeCause = StrEnum("PeriodChangeCause", enum_members(PERIOD_CHANGE_CAUSES))  # type: ignore[misc]
