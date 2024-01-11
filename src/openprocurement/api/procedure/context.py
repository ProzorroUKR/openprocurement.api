from copy import deepcopy

from openprocurement.api.context import get_request


def init_object(obj_name, obj_doc, config_serializer=None):
    request = get_request()
    request.validated[f"{obj_name}_src"] = obj_doc
    request.validated[obj_name] = deepcopy(request.validated[f"{obj_name}_src"])
    request.validated[f"{obj_name}_config"] = request.validated[obj_name].pop("config", None) or {}
    if config_serializer:
        request.validated[f"{obj_name}_config"] = config_serializer(request.validated[f"{obj_name}_config"]).data
    return request.validated[obj_name]
