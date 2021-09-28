from cornice.service import Service
from pyramid.response import Response
from openprocurement.api import constants
import datetime

constants_service = Service(name="constants", path="/constants", renderer="json")

blacklist = (
    "ADDITIONAL_CLASSIFICATIONS_SCHEMES",
    "ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017",
    "ATC_CODES",
    "ATC_SCHEME",
    "CONSTANTS_CONFIG",
    "CONSTANTS_FILE_PATH",
    "COORDINATES_REG_EXP",
    "COUNTRIES",
    "CPV_BLOCK_FROM",
    "CPV_CODES",
    "CPV_ITEMS_CLASS_FROM",
    "CPV_PHARM_PRODUCTS",
    "CURRENCIES",
    "DK_CODES",
    "DOCUMENT_BLACKLISTED_FIELDS",
    "DOCUMENT_WHITELISTED_FIELDS",
    "FUNDERS",
    "GMDN",
    "GMDN_CPV_PREFIXES",
    "GMDN_SCHEME",
    "GUARANTEE_ALLOWED_TENDER_TYPES",
    "HOLIDAYS",
    "INN_CODES",
    "INN_SCHEME",
    "JOURNAL_PREFIX",
    "LOGGER",
    "NORMALIZE_SHOULD_START_AFTER",
    "ORA_CODES",
    "ROUTE_PREFIX",
    "SANDBOX_MODE",
    "SCALE_CODES",
    "SCHEMA_DOC",
    "SCHEMA_VERSION",
    "SESSION",
    "TZ",
    "UA_REGIONS",
    "UA_ROAD",
    "UA_ROAD_CPV_PREFIXES",
    "UA_ROAD_SCHEME",
    "VERSION",
    "WORKING_DAYS",
)

@constants_service.get()
def get_constants(request):
    result = {}
    for k, v in constants.__dict__.items():
        if k not in blacklist:
            if k == k.upper():
                if isinstance(v, datetime.date):
                    result[k] = v.isoformat()
    return Response(json_body=result)
