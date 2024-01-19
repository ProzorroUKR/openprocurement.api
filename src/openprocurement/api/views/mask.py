import requests
from cornice.service import Service
from pyramid.response import Response

from openprocurement.api.mask import mask_data
from openprocurement.framework.core.procedure.mask import (
    SUBMISSION_MASK_MAPPING,
    QUALIFICATION_MASK_MAPPING,
    AGREEMENT_MASK_MAPPING,
)
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING

health = Service(name="mask", path="/mask", renderer="json")


@health.get()
def get_masked(request):
    url = request.params.get("url")
    response = requests.get(url)
    json = response.json()
    name = request.params.get("name")
    mapping = {
        "submission": SUBMISSION_MASK_MAPPING,
        "qualification": QUALIFICATION_MASK_MAPPING,
        "agreement": AGREEMENT_MASK_MAPPING,
        "tender": TENDER_MASK_MAPPING,
        "contract": CONTRACT_MASK_MAPPING,
    }
    mask_data(json["data"], TENDER_MASK_MAPPING)
    return Response(json_body=json, status=200)
