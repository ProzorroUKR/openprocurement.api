from typing import Union

from openprocurement.api.context import thread_context


def get_plan() -> Union[dict, None]:
    return thread_context.request.validated.get("plan")


def get_milestone() -> Union[dict, None]:
    return thread_context.request.validated.get("milestone")
