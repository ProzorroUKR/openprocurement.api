from copy import deepcopy

from openprocurement.api.context import get_request


def init_object(obj_name, obj, obj_src=None, config_serializer=None):
    request = get_request()
    request.validated[obj_name] = obj
    if obj_src is not None:
        request.validated[f"{obj_name}_src"] = obj_src
    else:
        request.validated[f"{obj_name}_src"] = deepcopy(request.validated[obj_name])
    request.validated[f"{obj_name}_config"] = request.validated[obj_name].pop("config", None) or {}
    if config_serializer:
        request.validated[f"{obj_name}_config"] = config_serializer(request.validated[f"{obj_name}_config"]).data
    return request.validated[obj_name]
