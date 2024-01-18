from typing import Union

from openprocurement.api.procedure.context import get_object


def get_plan() -> Union[dict, None]:
    return get_object("plan")


def get_milestone() -> Union[dict, None]:
    return get_object("milestone")
