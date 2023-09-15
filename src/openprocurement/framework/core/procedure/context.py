from typing import Union
from openprocurement.api.context import get_request


def get_object(obj_name="framework") -> Union[dict, None]:
    obj = get_request().validated.get(obj_name)
    return obj


def get_object_config(obj_name="framework") -> Union[dict, None]:
    obj = get_request().validated.get(f"{obj_name}_config", {})
    return obj
