import datetime

from cornice.service import Service
from pyramid.response import Response

from openprocurement.api import constants_env

constants_service = Service(name="constants", path="/constants", renderer="json")

blacklist = (
    "CONSTANTS_FILE_PATH",
    "CONSTANTS_CONFIG",
    "TENDER_CONFIG_OPTIONALITY",
    "CONFIDENTIAL_EDRPOU_LIST",
    "FAST_CATALOGUE_FLOW_FRAMEWORK_IDS",
    "BELOWTHRESHOLD_FUNDERS_IDS",
)


@constants_service.get()
def get_constants(request):
    result = {}
    for k, v in constants_env.__dict__.items():
        # Only include uppercase constants (standard naming convention)
        # and exclude blacklisted items
        if k.isupper() and k not in blacklist:
            if isinstance(v, datetime.date):
                result[k] = v.isoformat()
            else:
                result[k] = v
    return Response(json_body=result)
