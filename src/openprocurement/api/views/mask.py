import requests
from cornice.service import Service
from pyramid.response import Response

from openprocurement.api.mask import mask_data
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING

health = Service(name="mask", path="/mask", renderer="json")


@health.get()
def get_masked(request):
    url = request.params.get("url")
    response = requests.get(url)
    json = response.json()
    mask_data(json["data"], TENDER_MASK_MAPPING)
    return Response(json_body=json, status=200)
