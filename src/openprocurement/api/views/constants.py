from cornice.service import Service
from pyramid.response import Response

from openprocurement.api import constants_env
from openprocurement.api.utils import json_dumps

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
        # Exclude non-uppercase constants (standard naming convention)
        if not k.isupper():
            continue
        # Exclude blacklisted items
        if k in blacklist:
            continue
        # Include the constant in the result
        result[k] = v
    return Response(
        text=json_dumps(result),
        content_type="application/json",
    )
