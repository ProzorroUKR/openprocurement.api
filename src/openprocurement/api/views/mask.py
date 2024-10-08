import requests
from cornice.service import Service
from pyramid.response import Response

from openprocurement.api.mask import mask_data
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.framework.core.procedure.mask import (
    AGREEMENT_MASK_MAPPING,
    QUALIFICATION_MASK_MAPPING,
    SUBMISSION_MASK_MAPPING,
)
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING

health = Service(name="mask", path="/mask", renderer="json")


@health.get()
def get_masked(request):
    url = request.params.get("url")
    response = requests.get(url)
    json = response.json()
    mapping = {
        "submission": SUBMISSION_MASK_MAPPING,
        "qualification": QUALIFICATION_MASK_MAPPING,
        "agreement": AGREEMENT_MASK_MAPPING,
        "tender": TENDER_MASK_MAPPING,
        "contract": CONTRACT_MASK_MAPPING,
    }
    name = request.params.get("name")
    if name not in mapping:
        name = "tender"
    mask_data(json["data"], mapping[name])
    return Response(json_body=json, status=200)
