import os
import re
from datetime import time
from logging import getLogger

import standards
from pytz import timezone
from requests import Session

from openprocurement.api import constants_env
from openprocurement.api.constants_utils import (
    load_criteria_rules,
    parse_str_list,
    split_classifier_by_year,
)

# Logging
LOGGER = getLogger("openprocurement.api")

# Api route
VERSION = "2.5"
MAIN_ROUTE_PREFIX = "/api/{}".format(VERSION)
ROUTE_PREFIX = "" if os.environ.get("NO_SUB_APP_ROUTE_PREFIX") else MAIN_ROUTE_PREFIX

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

CONTRACT_GUARANTEE_ALLOWED_TENDER_TYPES = (
    "belowThreshold",
    "aboveThreshold",
    "competitiveOrdering",
    "aboveThresholdUA",
    "aboveThresholdEU",
    "esco",
    "priceQuotation",
    "competitiveDialogueUA.stage2",
    "competitiveDialogueEU.stage2",
    "closeFrameworkAgreementSelectionUA",
    "requestForProposal",
    "simple.defense",
)

BID_GUARANTEE_ALLOWED_TENDER_TYPES = (
    "belowThreshold",
    "aboveThreshold",
    "competitiveOrdering",
    "aboveThresholdUA",
    "aboveThresholdEU",
    "esco",
    "competitiveDialogueUA.stage2",
    "competitiveDialogueEU.stage2",
    "closeFrameworkAgreementUA",
    "closeFrameworkAgreementSelectionUA",
    "requestForProposal",
    "simple.defense",
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

# Calendar
WORKING_DAYS = {}
HOLIDAYS = standards.load("calendars/workdays_off.json")
for date_str in HOLIDAYS:
    WORKING_DAYS[date_str] = True

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
FUNDERS = [
    (i["identifier"]["scheme"], i["identifier"]["id"]) for i in standards.load("codelists/tender/tender_funder.json")
]

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

# Complaint objections classifications
ARTICLE_16 = {criterion["classification"]["id"] for criterion in standards.load("criteria/article_16.json")}
ARTICLE_17 = {criterion["classification"]["id"] for criterion in standards.load("criteria/article_17.json")}
OTHER_CRITERIA = {criterion["classification"]["id"] for criterion in standards.load("criteria/other.json")}

# additional criteria
CRITERION_LIFE_CYCLE_COST_IDS = {criterion["classification"]["id"] for criterion in standards.load("criteria/LCC.json")}
DECREE_1178 = {criterion["classification"]["id"] for criterion in standards.load("criteria/decree_1178.json")}
CRITERIA_UKRAINE_FACILITY = {
    criterion["classification"]["id"] for criterion in standards.load("criteria/ukraine_facility.json")
}

CRITERIA_LIST = (
    ARTICLE_16 | ARTICLE_17 | OTHER_CRITERIA | CRITERION_LIFE_CYCLE_COST_IDS | DECREE_1178 | CRITERIA_UKRAINE_FACILITY
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

TENDER_CO_CONFIG_JSONSCHEMAS = {
    "competitiveOrdering.long": standards.load("data_model/schema/TenderConfig/competitiveOrdering.long.json"),
    "competitiveOrdering.short": standards.load("data_model/schema/TenderConfig/competitiveOrdering.short.json"),
}

# Framework config
FRAMEWORK_CONFIG_JSONSCHEMAS = {
    "electronicCatalogue": standards.load("data_model/schema/FrameworkConfig/electronicCatalogue.json"),
    "dynamicPurchasingSystem": standards.load("data_model/schema/FrameworkConfig/dynamicPurchasingSystem.json"),
    "internationalFinancialInstitutions": standards.load(
        "data_model/schema/FrameworkConfig/internationalFinancialInstitutions.json"
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

# cause for reporting
TENDER_CAUSE = {
    key for key, desc in standards.load("codelists/tender/tender_cause.json").items() if desc["archive"] is False
}

TENDER_CAUSE_REPORTING = {}
TENDER_CAUSE_REPORTING_ALL = standards.load("codelists/tender/tender_cause_details/reporting.json")

for key, desc in TENDER_CAUSE_REPORTING_ALL.items():
    if desc["archive"] is False:
        TENDER_CAUSE_REPORTING[key] = desc

TENDER_CAUSE_NEGOTIATION = {}
TENDER_CAUSE_NEGOTIATION_ALL = standards.load("codelists/tender/tender_cause_details/negotiation.json")

for key, desc in TENDER_CAUSE_NEGOTIATION_ALL.items():
    if desc["archive"] is False:
        TENDER_CAUSE_NEGOTIATION[key] = desc

TENDER_CAUSE_NEGOTIATION_QUICK = {}
TENDER_CAUSE_NEGOTIATION_QUICK_ALL = standards.load("codelists/tender/tender_cause_details/negotiation.quick.json")

for key, desc in TENDER_CAUSE_NEGOTIATION_QUICK_ALL.items():
    if desc["archive"] is False:
        TENDER_CAUSE_NEGOTIATION_QUICK[key] = desc


# only active causes
CAUSE_DETAILS_MAPPING = {
    "reporting": TENDER_CAUSE_REPORTING,
    "negotiation": TENDER_CAUSE_NEGOTIATION,
    "negotiation.quick": TENDER_CAUSE_NEGOTIATION_QUICK,
}

CAUSE_DETAILS_MAPPING_ALL = {
    "reporting": TENDER_CAUSE_REPORTING_ALL,
    "negotiation": TENDER_CAUSE_NEGOTIATION_ALL,
    "negotiation.quick": TENDER_CAUSE_NEGOTIATION_QUICK_ALL,
}

# Should be at the end of the file for now
# TODO: move to modules initialization
TENDER_CRITERIA_RULES = {
    "aboveThreshold": load_criteria_rules("aboveThreshold", constants_env),
    "competitiveOrdering": load_criteria_rules("competitiveOrdering", constants_env),
    "aboveThresholdEU": load_criteria_rules("aboveThresholdEU", constants_env),
    "aboveThresholdUA.defense": load_criteria_rules("aboveThresholdUA.defense", constants_env),
    "aboveThresholdUA": load_criteria_rules("aboveThresholdUA", constants_env),
    "belowThreshold": load_criteria_rules("belowThreshold", constants_env),
    "closeFrameworkAgreementSelectionUA": load_criteria_rules("closeFrameworkAgreementSelectionUA", constants_env),
    "closeFrameworkAgreementUA": load_criteria_rules("closeFrameworkAgreementUA", constants_env),
    "competitiveDialogueEU": load_criteria_rules("competitiveDialogueEU", constants_env),
    "competitiveDialogueEU.stage2": load_criteria_rules("competitiveDialogueEU.stage2", constants_env),
    "competitiveDialogueUA": load_criteria_rules("competitiveDialogueUA", constants_env),
    "competitiveDialogueUA.stage2": load_criteria_rules("competitiveDialogueUA.stage2", constants_env),
    "esco": load_criteria_rules("esco", constants_env),
    "negotiation": load_criteria_rules("negotiation", constants_env),
    "negotiation.quick": load_criteria_rules("negotiation.quick", constants_env),
    "priceQuotation": load_criteria_rules("priceQuotation", constants_env),
    "reporting": load_criteria_rules("reporting", constants_env),
    "simple.defense": load_criteria_rules("simple.defense", constants_env),
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

# Language codes
LANGUAGE_CODES = standards.load("classifiers/languages.json").keys()

# CS-19019
PROFILE_REQUIRED_MIN_VALUE_AMOUNT = 500000

# CS-19545
BROKERS = {broker["name"]: broker["title"] for broker in standards.load("organizations/brokers.json")}

KIND_PROCUREMENT_METHOD_TYPE_MAPPING = standards.load("organizations/kind_procurementMethodType_mapping.json")
KIND_FRAMEWORK_TYPE_MAPPING = standards.load("organizations/kind_frameworkType_mapping.json")
