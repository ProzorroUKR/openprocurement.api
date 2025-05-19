from importlib.metadata import version

from cornice.service import Service
from pyramid.response import Response

constants_service = Service(name="version", path="/version", renderer="json")

STANDARDS_BASE_URL = "https://github.com/ProzorroUKR/standards/tree"


@constants_service.get()
def get_version(request):
    return Response(
        json_body={
            "API": version("openprocurement.api"),
            "standards": {
                "version": version("standards"),
                "url": f'{STANDARDS_BASE_URL}/{version("standards")}',
            },
        }
    )
