from cornice.service import Service
from pyramid.response import Response

health = Service(name="health", path="/health", renderer="json")


@health.get()
def get_spore(request):
    return Response(json_body={"health": "ok"}, status=200)
