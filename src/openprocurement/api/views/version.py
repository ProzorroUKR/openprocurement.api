from importlib.metadata import version

from cornice.service import Service
from pyramid.response import Response

constants_service = Service(name="version", path="/version", renderer="json")


@constants_service.get()
def get_version(request):
    return Response(
        json_body={
            "API": version("openprocurement.api"),
            "standards": version("standards"),
        }
    )
