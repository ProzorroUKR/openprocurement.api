# -*- coding: utf-8 -*-
import os
import re
from ConfigParser import ConfigParser, DEFAULTSECT

from iso8601 import parse_date
from pytz import timezone
from datetime import datetime
from logging import getLogger
from requests import Session

LOGGER = getLogger("openprocurement.api")
VERSION = "2.5"
ROUTE_PREFIX = "/api/{}".format(VERSION)
SESSION = Session()
SCHEMA_VERSION = 24
SCHEMA_DOC = "openprocurement_schema"

TZ = timezone(os.environ["TZ"] if "TZ" in os.environ else "Europe/Kiev")
SANDBOX_MODE = os.environ.get("SANDBOX_MODE", False)

DOCUMENT_BLACKLISTED_FIELDS = ("title", "format", "url", "dateModified", "hash")
DOCUMENT_WHITELISTED_FIELDS = ("id", "datePublished", "author", "__parent__")


def read_json(name):
    import os.path
    from json import loads

    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, name)
    with open(file_path) as lang_file:
        data = lang_file.read()
    return loads(data)


CPV_CODES = read_json("data/cpv.json")
CPV_CODES.append("99999999-9")
DK_CODES = read_json("data/dk021.json")
FUNDERS = [(i["scheme"], i["id"]) for i in read_json("data/funders.json")["data"]]
ORA_CODES = [i["code"] for i in read_json("data/organization_identifier_scheme.json")["data"]]
WORKING_DAYS = read_json("data/working_days.json")
GMDN = {k for k in read_json("data/gmdn.json").keys()}
GMDN_CPV_PREFIXES = read_json("data/gmdn_cpv_prefixes.json")
UA_ROAD = read_json("data/ua_road.json")
UA_ROAD_CPV_PREFIXES = read_json("data/ua_road_cpv_prefixes.json")

ATC_CODES = read_json("data/atc.json")
INN_CODES = read_json("data/inn.json")

ADDITIONAL_CLASSIFICATIONS_SCHEMES = [u"ДКПП", u"NONE", u"ДК003", u"ДК015", u"ДК018"]
ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017 = [u"ДК003", u"ДК015", u"ДК018", u"specialNorms"]

INN_SCHEME = "INN"
ATC_SCHEME = "ATC"
GMDN_SCHEME = "GMDN"
UA_ROAD_SCHEME = "UA-ROAD"

CPV_PHARM_PRODUCTS = "33600000-6"

COORDINATES_REG_EXP = re.compile(r"-?\d{1,3}\.\d+|-?\d{1,3}")

SCALE_CODES = ["micro", "sme", "mid", "large", "not specified"]

NORMALIZE_SHOULD_START_AFTER = datetime(2016, 7, 16, tzinfo=TZ)

CPV_ITEMS_CLASS_FROM = datetime(2017, 1, 1, tzinfo=TZ)
CPV_BLOCK_FROM = datetime(2017, 6, 2, tzinfo=TZ)

def get_default_constants_file_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "constants.ini")


def load_constants(file_path):
    config = ConfigParser()
    try:
        with open(file_path) as fp:
            config.readfp(fp)
    except Exception as e:
        raise type(e)(
            "Can't read file '{0}': use current path or override using "
            "CONSTANTS_FILE_PATH env variable".format(file_path)
        )
    return config


def parse_date_tz(datestring):
    return parse_date(datestring, TZ)


def get_constant(config, constant, section=DEFAULTSECT, parse_func=parse_date_tz):
    return parse_func(os.environ.get("{}_{}".format(section, constant)) or config.get(section, constant))


CONSTANTS_FILE_PATH = os.environ.get("CONSTANTS_FILE_PATH", get_default_constants_file_path())
CONSTANTS_CONFIG = load_constants(CONSTANTS_FILE_PATH)

BUDGET_PERIOD_FROM = get_constant(CONSTANTS_CONFIG, "BUDGET_PERIOD_FROM")

# Set non required additionalClassification for classification_id 999999-9
NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM = get_constant(
    CONSTANTS_CONFIG, "NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM"
)

# Set INN additionalClassification validation required
CPV_336_INN_FROM = get_constant(CONSTANTS_CONFIG, "CPV_336_INN_FROM")

JOURNAL_PREFIX = os.environ.get("JOURNAL_PREFIX", "JOURNAL_")

# Add scale field to organization
ORGANIZATION_SCALE_FROM = get_constant(CONSTANTS_CONFIG, "ORGANIZATION_SCALE_FROM")

# Add vat validation
VAT_FROM = get_constant(CONSTANTS_CONFIG, "VAT_FROM")

# Set mainProcurementCategory required
MPC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "MPC_REQUIRED_FROM")

MILESTONES_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "MILESTONES_VALIDATION_FROM")

# Plan.buyers required
PLAN_BUYERS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "PLAN_BUYERS_REQUIRED_FROM")

# negotiation.quick cause required
QUICK_CAUSE_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "QUICK_CAUSE_REQUIRED_FROM")

# Budget breakdown required from
BUDGET_BREAKDOWN_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "BUDGET_BREAKDOWN_REQUIRED_FROM")

# Business date calculation first non working day midnight allowed from
WORKING_DATE_ALLOW_MIDNIGHT_FROM = get_constant(CONSTANTS_CONFIG, "WORKING_DATE_ALLOW_MIDNIGHT_FROM")

NORMALIZED_CLARIFICATIONS_PERIOD_FROM = get_constant(CONSTANTS_CONFIG, "NORMALIZED_CLARIFICATIONS_PERIOD_FROM")

RELEASE_2020_04_19 = get_constant(CONSTANTS_CONFIG, "RELEASE_2020_04_19")

# CS-6687 make required complaint identifier fields for tenders created from
COMPLAINT_IDENTIFIER_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "COMPLAINT_IDENTIFIER_REQUIRED_FROM")

# CS-7231 new negotiation causes released (old partly disabled)
NEW_NEGOTIATION_CAUSES_FROM = get_constant(CONSTANTS_CONFIG, "NEW_NEGOTIATION_CAUSES_FROM")

# CS-8167 tender/lot minimalStep validation
MINIMAL_STEP_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "MINIMAL_STEP_VALIDATION_FROM")

# Address validation
COUNTRIES = read_json("data/countries.json")
UA_REGIONS = read_json("data/ua_regions.json")
VALIDATE_ADDRESS_FROM = get_constant(CONSTANTS_CONFIG, "VALIDATE_ADDRESS_FROM")

# address and kind fields required for procuringEntity and buyers objects in plan
PLAN_ADDRESS_KIND_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "PLAN_ADDRESS_KIND_REQUIRED_FROM")

NORMALIZED_TENDER_PERIOD_FROM = get_constant(CONSTANTS_CONFIG, "NORMALIZED_TENDER_PERIOD_FROM")
RELEASE_ECRITERIA_ARTICLE_17 = get_constant(CONSTANTS_CONFIG, "RELEASE_ECRITERIA_ARTICLE_17")
