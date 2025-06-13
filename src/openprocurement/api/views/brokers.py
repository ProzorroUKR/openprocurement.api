from cornice.service import Service
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.response import Response

from openprocurement.api.constants import BROKERS

constants_service = Service(name="brokers", path="/brokers", renderer="json")


@constants_service.get()
def get_brokers(request):
    filtered_levels = []
    if levels := request.params.get("levels"):
        filtered_levels = levels.split(",")
    policy = request.registry.queryUtility(IAuthenticationPolicy)
    users = []
    for user_data in policy.users.values():
        if user_data["group"] == "brokers":
            if filtered_levels and not any(level in user_data["level"] for level in filtered_levels):
                continue
            levels = []
            permissions = []
            for symb in list(user_data["level"]):
                if symb.isdigit():
                    levels.append(int(symb))
                else:
                    permissions.append(symb)
            users.append(
                {
                    "name": user_data["name"],
                    "title": broker_title if (broker_title := BROKERS.get(user_data["name"])) else user_data["name"],
                    "levels": levels,
                    "permissions": permissions,
                }
            )
    return Response(json_body=users)
