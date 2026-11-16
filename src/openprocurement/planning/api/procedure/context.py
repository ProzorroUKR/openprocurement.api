from openprocurement.api.procedure.context import get_object


def get_plan() -> dict | None:
    return get_object("plan")


def get_milestone() -> dict | None:
    return get_object("milestone")
