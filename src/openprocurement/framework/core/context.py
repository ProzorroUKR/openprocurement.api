from typing import Union

from openprocurement.api.context import get_request


def get_framework() -> Union[dict, None]:
    framework = get_request().validated.get("framework")
    return framework
