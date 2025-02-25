import os
import re
from configparser import DEFAULTSECT, ConfigParser
from datetime import time
from logging import getLogger

import standards
from ciso8601 import parse_datetime
from pytz import timezone
from requests import Session

from openprocurement.api.constants_utils import load_criteria_rules

LOGGER = getLogger("openprocurement.api")
VERSION = "2.5"
ROUTE_PREFIX = "/api/{}".format(VERSION)
SESSION = Session()
OCID_PREFIX = os.environ.get("OCID_PREFIX", "ocds-be6bcu")

TZ = timezone(os.environ["TZ"] if "TZ" in os.environ else "Europe/Kiev")
SANDBOX_MODE = os.environ.get("SANDBOX_MODE", False)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Tenders in which could be used criteria connected with guarantee
GUARANTEE_ALLOWED_TENDER_TYPES = (
    "belowThreshold",
    "aboveThreshold",
    "competitiveOrdering",
    "aboveThresholdUA",
    "aboveThresholdEU",
    "esco",
    "priceQuotation",
    "competitiveDialogueUA",
    "competitiveDialogueEU",
    "competitiveDialogueUA.stage2",
    "competitiveDialogueEU.stage2",
    "closeFrameworkAgreementUA",
    "closeFrameworkAgreementSelectionUA",
    "requestForProposal",
)

BID_REQUIRED_ITEMS_TENDER_TYPES = (
    "belowThreshold",
    "aboveThreshold",
    "competitiveOrdering",
    "aboveThresholdUA",
    "aboveThresholdEU",
    "competitiveDialogueUA",
    "competitiveDialogueEU",
    "competitiveDialogueUA.stage2",
    "competitiveDialogueEU.stage2",
    "closeFrameworkAgreementUA",
    "closeFrameworkAgreementSelectionUA",
    "esco",
    "priceQuotation",
    "requestForProposal",
)

WORKING_DAYS = {}
HOLIDAYS = standards.load("calendars/workdays_off.json")
for date_str in HOLIDAYS:
    WORKING_DAYS[date_str] = True


def parse_str_list(value):
    return [x.strip() for x in value.split(",") if x.strip()]


DEPRECATED_FEED_USER_AGENTS = parse_str_list(os.environ.get("DEPRECATED_FEED_USER_AGENTS", ""))

TENDER_PERIOD_START_DATE_STALE_MINUTES = int(os.environ.get("TENDER_PERIOD_START_DATE_STALE_MINUTES", 10))

CPV_PHARM_PRODUCTS = "33600000-6"
CPV_NOT_CPV = "99999999-9"

CPV_PREFIX_LENGTH_TO_NAME = {
    3: "group",
    4: "class",
    5: "category",
    6: "subcategory",
}

CPV_CODES = list(standards.load("classifiers/cpv_en.json"))
CPV_CODES.append(CPV_NOT_CPV)
DK_CODES = list(standards.load("classifiers/dk021_uk.json"))
FUNDERS = [
    (i["identifier"]["scheme"], i["identifier"]["id"]) for i in standards.load("codelists/tender/tender_funder.json")
]
ORA_CODES = [i["code"] for i in standards.load("organizations/identifier_scheme.json")["data"]]
# extended keys gmdn contains actual and obsolete codes, since deleted codes can block un-refactored endpoints
GMDN_2019 = set(standards.load("classifiers/gmdn.json"))
GMDN_2023 = set(standards.load("classifiers/gmdn_2023.json"))
GMDN_CPV_PREFIXES = standards.load("classifiers/gmdn_cpv_prefixes.json")
UA_ROAD = standards.load("classifiers/ua_road.json")
UA_ROAD_CPV_PREFIXES = standards.load("classifiers/ua_road_cpv_prefixes.json")
CCCE_UA = standards.load("classifiers/ccce_ua.json")
KPKV_UK = standards.load("classifiers/kpkv_uk_2025.json")
KEKV_UK = standards.load("classifiers/kekv_uk.json")

# complaint objections classifications
ARTICLE_16 = {criterion["classification"]["id"] for criterion in standards.load("criteria/article_16.json")}
ARTICLE_17 = {criterion["classification"]["id"] for criterion in standards.load("criteria/article_17.json")}
OTHER_CRITERIA = {criterion["classification"]["id"] for criterion in standards.load("criteria/other.json")}
VIOLATION_AMCU = set(standards.load("AMCU/violation_amcu.json"))
AMCU = set(standards.load("AMCU/amcu.json"))
AMCU_24 = set(standards.load("AMCU/amcu_24.json"))
REQUESTED_REMEDIES_TYPES = set(standards.load("AMCU/requested_remedies_type.json"))

ADDITIONAL_CLASSIFICATIONS_SCHEMES = ["ДК003", "ДК015", "ДК018", "specialNorms"]

INN_SCHEME = "INN"
ATC_SCHEME = "ATC"
GMDN_2019_SCHEME = "GMDN"
GMDN_2023_SCHEME = "GMDN-2023"
UA_ROAD_SCHEME = "UA-ROAD"
CCCE_UA_SCHEME = "CCCE-UA"
KPKV_UK_SCHEME = "КПКВ"
KEKV_UK_SCHEME = "КЕКВ"

COORDINATES_REG_EXP = re.compile(r"-?\d{1,3}\.\d+|-?\d{1,3}")

SCALE_CODES = ["micro", "sme", "mid", "large", "not specified"]

TENDER_CONFIG_JSONSCHEMAS = {
    "aboveThreshold": standards.load("data_model/schema/TenderConfig/aboveThreshold.json"),
    "competitiveOrdering": standards.load("data_model/schema/TenderConfig/competitiveOrdering.json"),
    "aboveThresholdEU": standards.load("data_model/schema/TenderConfig/aboveThresholdEU.json"),
    "aboveThresholdUA.defense": standards.load("data_model/schema/TenderConfig/aboveThresholdUA.defense.json"),
    "aboveThresholdUA": standards.load("data_model/schema/TenderConfig/aboveThresholdUA.json"),
    "belowThreshold": standards.load("data_model/schema/TenderConfig/belowThreshold.json"),
    "closeFrameworkAgreementSelectionUA": standards.load(
        "data_model/schema/TenderConfig/closeFrameworkAgreementSelectionUA.json"
    ),
    "closeFrameworkAgreementUA": standards.load("data_model/schema/TenderConfig/closeFrameworkAgreementUA.json"),
    "competitiveDialogueEU": standards.load("data_model/schema/TenderConfig/competitiveDialogueEU.json"),
    "competitiveDialogueEU.stage2": standards.load("data_model/schema/TenderConfig/competitiveDialogueEU.stage2.json"),
    "competitiveDialogueUA": standards.load("data_model/schema/TenderConfig/competitiveDialogueUA.json"),
    "competitiveDialogueUA.stage2": standards.load("data_model/schema/TenderConfig/competitiveDialogueUA.stage2.json"),
    "esco": standards.load("data_model/schema/TenderConfig/esco.json"),
    "negotiation": standards.load("data_model/schema/TenderConfig/negotiation.json"),
    "negotiation.quick": standards.load("data_model/schema/TenderConfig/negotiation.quick.json"),
    "priceQuotation": standards.load("data_model/schema/TenderConfig/priceQuotation.json"),
    "reporting": standards.load("data_model/schema/TenderConfig/reporting.json"),
    "simple.defense": standards.load("data_model/schema/TenderConfig/simple.defense.json"),
    "requestForProposal": standards.load("data_model/schema/TenderConfig/requestForProposal.json"),
}

FRAMEWORK_CONFIG_JSONSCHEMAS = {
    "electronicCatalogue": standards.load("data_model/schema/FrameworkConfig/electronicCatalogue.json"),
    "dynamicPurchasingSystem": standards.load("data_model/schema/FrameworkConfig/dynamicPurchasingSystem.json"),
    "internationalFinancialInstitutions": standards.load(
        "data_model/schema/FrameworkConfig/internationalFinancialInstitutions.json"
    ),
}


def get_default_constants_file_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "constants.ini")


def load_constants(file_path):
    config = ConfigParser()
    try:
        with open(file_path) as fp:
            config.readfp(fp)
    except Exception as e:
        raise type(e)(
            "Can't read file '{}': use current path or override using CONSTANTS_FILE_PATH env variable".format(
                file_path
            )
        )
    return config


def parse_date(value):
    date = parse_datetime(value)
    if not date.tzinfo:
        date = TZ.localize(date)
    return date


def parse_bool(value):
    if str(value).lower() in ("yes", "y", "true", "t", "1"):
        return True
    if str(value).lower() in (
        "no",
        "n",
        "false",
        "f",
        "0",
        "0.0",
        "",
        "none",
        "[]",
        "{}",
    ):
        return False
    raise ValueError("Invalid value for boolean conversion: " + str(value))


def get_constant(config, constant, section=DEFAULTSECT, parse_func=parse_date):
    return parse_func(os.environ.get("{}_{}".format(section, constant)) or config.get(section, constant))


JOURNAL_PREFIX = os.environ.get("JOURNAL_PREFIX", "JOURNAL_")


CONSTANTS_FILE_PATH = os.environ.get("CONSTANTS_FILE_PATH", get_default_constants_file_path())
CONSTANTS_CONFIG = load_constants(CONSTANTS_FILE_PATH)

VALIDATE_ADDRESS_FROM = get_constant(CONSTANTS_CONFIG, "VALIDATE_ADDRESS_FROM")

BUDGET_PERIOD_FROM = get_constant(CONSTANTS_CONFIG, "BUDGET_PERIOD_FROM")

# Set mainProcurementCategory required
MPC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "MPC_REQUIRED_FROM")

MILESTONES_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "MILESTONES_VALIDATION_FROM")

# Plan.buyers required
PLAN_BUYERS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "PLAN_BUYERS_REQUIRED_FROM")

# negotiation.quick cause required
QUICK_CAUSE_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "QUICK_CAUSE_REQUIRED_FROM")

# Budget breakdown required from
BUDGET_BREAKDOWN_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "BUDGET_BREAKDOWN_REQUIRED_FROM")

RELEASE_2020_04_19 = get_constant(CONSTANTS_CONFIG, "RELEASE_2020_04_19")

# CS-6687 make required complaint identifier fields for tenders created from
COMPLAINT_IDENTIFIER_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "COMPLAINT_IDENTIFIER_REQUIRED_FROM")

# CS-7231 new negotiation causes released (old partly disabled)
NEW_NEGOTIATION_CAUSES_FROM = get_constant(CONSTANTS_CONFIG, "NEW_NEGOTIATION_CAUSES_FROM")

# CS-8167 tender/lot minimalStep validation
MINIMAL_STEP_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "MINIMAL_STEP_VALIDATION_FROM")

# CS-11442 contract/items/additionalClassifications scheme: COO
COUNTRIES_MAP = standards.load("classifiers/countries.json")

# Address validation
COUNTRIES = {c["name_uk"] for c in COUNTRIES_MAP.values()}
UA_REGIONS = standards.load("classifiers/ua_regions.json")

# address and kind fields required for procuringEntity and buyers objects in plan
PLAN_ADDRESS_KIND_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "PLAN_ADDRESS_KIND_REQUIRED_FROM")

RELEASE_ECRITERIA_ARTICLE_17 = get_constant(CONSTANTS_CONFIG, "RELEASE_ECRITERIA_ARTICLE_17")

# CS-8383 add requirement status and versioning
CRITERION_REQUIREMENT_STATUSES_FROM = get_constant(CONSTANTS_CONFIG, "CRITERION_REQUIREMENT_STATUSES_FROM")

RELEASE_SIMPLE_DEFENSE_FROM = get_constant(CONSTANTS_CONFIG, "RELEASE_SIMPLE_DEFENSE_FROM")

# CS-8981 new complaints in openuadefense
NEW_DEFENSE_COMPLAINTS_FROM = get_constant(CONSTANTS_CONFIG, "NEW_DEFENSE_COMPLAINTS_FROM")
NEW_DEFENSE_COMPLAINTS_TO = get_constant(CONSTANTS_CONFIG, "NEW_DEFENSE_COMPLAINTS_TO")

# CS-8981 award claims restricted in openuadefense
NO_DEFENSE_AWARD_CLAIMS_FROM = get_constant(CONSTANTS_CONFIG, "NO_DEFENSE_AWARD_CLAIMS_FROM")

# CS-8595 two phase commit
TWO_PHASE_COMMIT_FROM = get_constant(CONSTANTS_CONFIG, "TWO_PHASE_COMMIT_FROM")

# CS-9327 guarantee support
RELEASE_GUARANTEE_CRITERION_FROM = get_constant(CONSTANTS_CONFIG, "RELEASE_GUARANTEE_CRITERION_FROM")

# CS-9158 metrics support
RELEASE_METRICS_FROM = get_constant(CONSTANTS_CONFIG, "RELEASE_METRICS_FROM")

# CS-8330 validation for ContactPoint.telephone
VALIDATE_TELEPHONE_FROM = get_constant(CONSTANTS_CONFIG, "VALIDATE_TELEPHONE_FROM")

# CS-9333 unit object required for item
UNIT_PRICE_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "UNIT_PRICE_REQUIRED_FROM")

# CS-10431 validation currency
CURRENCIES = standards.load("codelists/tender/tender_currency.json")
VALIDATE_CURRENCY_FROM = get_constant(CONSTANTS_CONFIG, "VALIDATE_CURRENCY_FROM")

# CS-10207 multi contracts required for multi buyers
MULTI_CONTRACTS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "MULTI_CONTRACTS_REQUIRED_FROM")

# CS-11411 multi profile available for pq tenders
PQ_MULTI_PROFILE_FROM = get_constant(CONSTANTS_CONFIG, "PQ_MULTI_PROFILE_FROM")

# CS-11856 hash criteria id
PQ_CRITERIA_ID_FROM = get_constant(CONSTANTS_CONFIG, "PQ_CRITERIA_ID_FROM")

# Decided in CS-8167
MINIMAL_STEP_VALIDATION_PRESCISSION = 2
MINIMAL_STEP_VALIDATION_LOWER_LIMIT = 0.005
MINIMAL_STEP_VALIDATION_UPPER_LIMIT = 0.03


# Masking
MASK_OBJECT_DATA_SINGLE = get_constant(CONSTANTS_CONFIG, "MASK_OBJECT_DATA_SINGLE", parse_func=parse_bool)

# CS-12463
FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM = get_constant(CONSTANTS_CONFIG, "FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM")

# CS-12553
FAST_CATALOGUE_FLOW_FRAMEWORK_IDS = get_constant(
    CONSTANTS_CONFIG,
    "FAST_CATALOGUE_FLOW_FRAMEWORK_IDS",
    parse_func=parse_str_list,
)

# Tender config optionality
TENDER_CONFIG_OPTIONALITY = {
    "hasAuction": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_AUCTION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasAwardingOrder": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_AWARDING_ORDER_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasValueRestriction": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_VALUE_RESTRICTION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "valueCurrencyEquality": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_VALUE_CURRENCY_EQUALITY",
        parse_func=parse_bool,
    ),
    "hasPrequalification": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_PREQUALIFICATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "minBidsNumber": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_MIN_BIDS_NUMBER_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasPreSelectionAgreement": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_PRE_SELECTION_AGREEMENT_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasTenderComplaints": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_COMPLAINTS_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasAwardComplaints": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_COMPLAINTS_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasCancellationComplaints": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_COMPLAINTS_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasValueEstimation": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_VALUE_ESTIMATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasQualificationComplaints": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_QUALIFICATION_COMPLAINTS_OPTIONAL",
        parse_func=parse_bool,
    ),
    "tenderComplainRegulation": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_COMPLAIN_REGULATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "qualificationComplainDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_QUALIFICATION_COMPLAIN_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "awardComplainDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_AWARD_COMPLAIN_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "cancellationComplainDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_CANCELLATION_COMPLAIN_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "clarificationUntilDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_CLARIFICATION_UNTIL_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "qualificationDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_QUALIFICATION_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "restricted": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_RESTRICTED_OPTIONAL",
        parse_func=parse_bool,
    ),
}

# Tender weightedValue pre-calculation on switch to active.auction
TENDER_WEIGHTED_VALUE_PRE_CALCULATION = get_constant(
    CONSTANTS_CONFIG,
    "TENDER_WEIGHTED_VALUE_PRE_CALCULATION",
    parse_func=parse_bool,
)

ECONTRACT_SIGNER_INFO_REQUIRED = get_constant(
    CONSTANTS_CONFIG,
    "ECONTRACT_SIGNER_INFO_REQUIRED",
    parse_func=parse_bool,
)

# Contract templates

CONTRACT_TEMPLATES_KEYS = standards.load("templates/contract_templates_keys.json")

# Related lot is required

RELATED_LOT_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "RELATED_LOT_REQUIRED_FROM")

# DST (daylight saving time) aware periods from
DST_AWARE_PERIODS_FROM = get_constant(CONSTANTS_CONFIG, "DST_AWARE_PERIODS_FROM")

# New qualification flow
QUALIFICATION_AFTER_COMPLAINT_FROM = get_constant(CONSTANTS_CONFIG, "QUALIFICATION_AFTER_COMPLAINT_FROM")

# Logging headers Authorization and X-Request-ID during each request
CRITICAL_HEADERS_LOG_ENABLED = get_constant(CONSTANTS_CONFIG, "CRITICAL_HEADERS_LOG_ENABLED", parse_func=parse_bool)

OBJECTIONS_ADDITIONAL_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "OBJECTIONS_ADDITIONAL_VALIDATION_FROM")
MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM = get_constant(
    CONSTANTS_CONFIG, "MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM"
)

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

# cause for reporting
TENDER_CAUSE = {
    key for key, desc in standards.load("codelists/tender/tender_cause.json").items() if desc["archive"] is False
}

# CS-16168
NOTICE_DOC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "NOTICE_DOC_REQUIRED_FROM")
# CS-16894
EVALUATION_REPORTS_DOC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "EVALUATION_REPORTS_DOC_REQUIRED_FROM")

CONTRACT_CONFIDENTIAL_DOCS_FROM = get_constant(CONSTANTS_CONFIG, "CONTRACT_CONFIDENTIAL_DOCS_FROM")


# CS-17490
AWARD_NOTICE_DOC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "AWARD_NOTICE_DOC_REQUIRED_FROM")

CRITERIA_CLASSIFICATION_UNIQ_FROM = get_constant(CONSTANTS_CONFIG, "CRITERIA_CLASSIFICATION_UNIQ_FROM")


CONFIDENTIAL_EDRPOU_LIST = get_constant(
    CONSTANTS_CONFIG,
    "CONFIDENTIAL_EDRPOU_LIST",
    parse_func=parse_str_list,
)

# CS-17904
CRITERIA_ARTICLE_16_REQUIRED = get_constant(CONSTANTS_CONFIG, "CRITERIA_ARTICLE_16_REQUIRED")

# CS-18305
NEW_ARTICLE_17_CRITERIA_REQUIRED = get_constant(CONSTANTS_CONFIG, "NEW_ARTICLE_17_CRITERIA_REQUIRED")

# Should be at the end of the file for now
# TODO: move to modules initialization
TENDER_CRITERIA_RULES = {
    "aboveThreshold": load_criteria_rules("aboveThreshold", globals()),
    "competitiveOrdering": load_criteria_rules("competitiveOrdering", globals()),
    "aboveThresholdEU": load_criteria_rules("aboveThresholdEU", globals()),
    "aboveThresholdUA.defense": load_criteria_rules("aboveThresholdUA.defense", globals()),
    "aboveThresholdUA": load_criteria_rules("aboveThresholdUA", globals()),
    "belowThreshold": load_criteria_rules("belowThreshold", globals()),
    "closeFrameworkAgreementSelectionUA": load_criteria_rules("closeFrameworkAgreementSelectionUA", globals()),
    "closeFrameworkAgreementUA": load_criteria_rules("closeFrameworkAgreementUA", globals()),
    "competitiveDialogueEU": load_criteria_rules("competitiveDialogueEU", globals()),
    "competitiveDialogueEU.stage2": load_criteria_rules("competitiveDialogueEU.stage2", globals()),
    "competitiveDialogueUA": load_criteria_rules("competitiveDialogueUA", globals()),
    "competitiveDialogueUA.stage2": load_criteria_rules("competitiveDialogueUA.stage2", globals()),
    "esco": load_criteria_rules("esco", globals()),
    "negotiation": load_criteria_rules("negotiation", globals()),
    "negotiation.quick": load_criteria_rules("negotiation.quick", globals()),
    "priceQuotation": load_criteria_rules("priceQuotation", globals()),
    "reporting": load_criteria_rules("reporting", globals()),
    "simple.defense": load_criteria_rules("simple.defense", globals()),
}

# CS-18389
BID_ITEMS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "BID_ITEMS_REQUIRED_FROM")

# CS-17925
REQ_RESPONSE_VALUES_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "REQ_RESPONSE_VALUES_VALIDATION_FROM")

# CS-17920, CS-18251
NEW_REQUIREMENTS_RULES_FROM = get_constant(CONSTANTS_CONFIG, "NEW_REQUIREMENTS_RULES_FROM")

# CS-18784
ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM")


AUCTION_DAY_START = time(11, 0)
AUCTION_DAY_END = time(16, 0)
HALF_HOUR_SECONDS = 30 * 60

# simplified way to get nuber of half-hours fit in period
# (it does not include minutes)
AUCTION_TIME_SLOTS_NUMBER = (AUCTION_DAY_END.hour - AUCTION_DAY_START.hour) * 2

PLAN_OF_UKRAINE = standards.load("classifiers/plan_of_ukraine.json")
