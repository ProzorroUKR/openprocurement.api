import os

from openprocurement.api.constants_utils import (
    get_constant,
    get_default_constants_file_path,
    load_constants,
    parse_bool,
    parse_str_list,
)

CONSTANTS_FILE_PATH = os.environ.get("CONSTANTS_FILE_PATH", get_default_constants_file_path())
CONSTANTS_CONFIG = load_constants(CONSTANTS_FILE_PATH)

VALIDATE_ADDRESS_FROM = get_constant(CONSTANTS_CONFIG, "VALIDATE_ADDRESS_FROM")

BUDGET_PERIOD_FROM = get_constant(CONSTANTS_CONFIG, "BUDGET_PERIOD_FROM")

MPC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "MPC_REQUIRED_FROM")

MILESTONES_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "MILESTONES_VALIDATION_FROM")

PLAN_BUYERS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "PLAN_BUYERS_REQUIRED_FROM")

# negotiation.quick cause required
QUICK_CAUSE_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "QUICK_CAUSE_REQUIRED_FROM")

BUDGET_BREAKDOWN_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "BUDGET_BREAKDOWN_REQUIRED_FROM")

RELEASE_2020_04_19 = get_constant(CONSTANTS_CONFIG, "RELEASE_2020_04_19")

# CS-6687 make required complaint identifier fields for tenders created from
COMPLAINT_IDENTIFIER_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "COMPLAINT_IDENTIFIER_REQUIRED_FROM")

# CS-7231 new negotiation causes released (old partly disabled)
NEW_NEGOTIATION_CAUSES_FROM = get_constant(CONSTANTS_CONFIG, "NEW_NEGOTIATION_CAUSES_FROM")

# CS-8167 tender/lot minimalStep validation
MINIMAL_STEP_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "MINIMAL_STEP_VALIDATION_FROM")

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
VALIDATE_CURRENCY_FROM = get_constant(CONSTANTS_CONFIG, "VALIDATE_CURRENCY_FROM")

# CS-10207 multi contracts required for multi buyers
MULTI_CONTRACTS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "MULTI_CONTRACTS_REQUIRED_FROM")

# CS-11411 multi profile available for pq tenders
PQ_MULTI_PROFILE_FROM = get_constant(CONSTANTS_CONFIG, "PQ_MULTI_PROFILE_FROM")

# CS-11856 hash criteria id
PQ_CRITERIA_ID_FROM = get_constant(CONSTANTS_CONFIG, "PQ_CRITERIA_ID_FROM")

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
    "minTenderingDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_MIN_TENDERING_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "hasEnquiries": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_HAS_ENQUIRIES_OPTIONAL",
        parse_func=parse_bool,
    ),
    "minEnquiriesDuration": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_MIN_ENQUIRIES_DURATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "enquiryPeriodRegulation": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_ENQUIRY_PERIOD_REGULATION_OPTIONAL",
        parse_func=parse_bool,
    ),
    "restricted": get_constant(
        CONSTANTS_CONFIG,
        "TENDER_CONFIG_RESTRICTED_OPTIONAL",
        parse_func=parse_bool,
    ),
}

# Related lot is required
RELATED_LOT_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "RELATED_LOT_REQUIRED_FROM")

# DST (daylight saving time) aware periods from
DST_AWARE_PERIODS_FROM = get_constant(CONSTANTS_CONFIG, "DST_AWARE_PERIODS_FROM")

# New qualification flow
QUALIFICATION_AFTER_COMPLAINT_FROM = get_constant(CONSTANTS_CONFIG, "QUALIFICATION_AFTER_COMPLAINT_FROM")

CONFIDENTIAL_EDRPOU_LIST = get_constant(
    CONSTANTS_CONFIG,
    "CONFIDENTIAL_EDRPOU_LIST",
    parse_func=parse_str_list,
)

# Logging headers Authorization and X-Request-ID during each request
CRITICAL_HEADERS_LOG_ENABLED = get_constant(
    CONSTANTS_CONFIG,
    "CRITICAL_HEADERS_LOG_ENABLED",
    parse_func=parse_bool,
)

OBJECTIONS_ADDITIONAL_VALIDATION_FROM = get_constant(
    CONSTANTS_CONFIG,
    "OBJECTIONS_ADDITIONAL_VALIDATION_FROM",
)

MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM = get_constant(
    CONSTANTS_CONFIG,
    "MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
)

# CS-16168
NOTICE_DOC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "NOTICE_DOC_REQUIRED_FROM")

# CS-16894
EVALUATION_REPORTS_DOC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "EVALUATION_REPORTS_DOC_REQUIRED_FROM")

CONTRACT_CONFIDENTIAL_DOCS_FROM = get_constant(CONSTANTS_CONFIG, "CONTRACT_CONFIDENTIAL_DOCS_FROM")

# CS-17490
AWARD_NOTICE_DOC_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "AWARD_NOTICE_DOC_REQUIRED_FROM")

CRITERIA_CLASSIFICATION_UNIQ_FROM = get_constant(CONSTANTS_CONFIG, "CRITERIA_CLASSIFICATION_UNIQ_FROM")

# CS-17904
CRITERIA_ARTICLE_16_REQUIRED = get_constant(CONSTANTS_CONFIG, "CRITERIA_ARTICLE_16_REQUIRED")

# CS-18305
NEW_ARTICLE_17_CRITERIA_REQUIRED = get_constant(CONSTANTS_CONFIG, "NEW_ARTICLE_17_CRITERIA_REQUIRED")

# CS-18389
BID_ITEMS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "BID_ITEMS_REQUIRED_FROM")

# CS-17925
REQ_RESPONSE_VALUES_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "REQ_RESPONSE_VALUES_VALIDATION_FROM")

# CS-17920, CS-18251
NEW_REQUIREMENTS_RULES_FROM = get_constant(CONSTANTS_CONFIG, "NEW_REQUIREMENTS_RULES_FROM")

# CS-18784
ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM")

# CS-19069
BELOWTHRESHOLD_FUNDERS_IDS = get_constant(
    CONSTANTS_CONFIG,
    "BELOWTHRESHOLD_FUNDERS_IDS",
    parse_func=parse_str_list,
)

# CS-16556
CRITERIA_CLASSIFICATION_VALIDATION_FROM = get_constant(CONSTANTS_CONFIG, "CRITERIA_CLASSIFICATION_VALIDATION_FROM")

# CS-19018
UKRAINE_FACILITY_CLASSIFICATIONS_REQUIRED_FROM = get_constant(
    CONSTANTS_CONFIG,
    "UKRAINE_FACILITY_CLASSIFICATIONS_REQUIRED_FROM",
)

# CS-19064
BID_ITEMS_PRODUCT_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "BID_ITEMS_PRODUCT_REQUIRED_FROM")

# CS-18575
TENDER_SIGNER_INFO_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "TENDER_SIGNER_INFO_REQUIRED_FROM")

# CS-19545
CONTRACT_OWNER_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "CONTRACT_OWNER_REQUIRED_FROM")

# CS-19960
MINIMAL_STEP_TENDERS_WITH_LOTS_VALIDATION_FROM = get_constant(
    CONSTANTS_CONFIG,
    "MINIMAL_STEP_TENDERS_WITH_LOTS_VALIDATION_FROM",
)

SIGNATURE_VERIFICATION_ENABLED = get_constant(
    CONSTANTS_CONFIG,
    "SIGNATURE_VERIFICATION_ENABLED",
    parse_func=parse_bool,
)

# CS-20345
ITEM_QUANTITY_REQUIRED_FROM = get_constant(
    CONSTANTS_CONFIG,
    "ITEM_QUANTITY_REQUIRED_FROM",
)

# CS-20144
UNIFIED_CRITERIA_LOGIC_FROM = get_constant(
    CONSTANTS_CONFIG,
    "UNIFIED_CRITERIA_LOGIC_FROM",
)

# CS-20470
CAUSE_DETAILS_REQUIRED_FROM = get_constant(CONSTANTS_CONFIG, "CAUSE_DETAILS_REQUIRED_FROM")
