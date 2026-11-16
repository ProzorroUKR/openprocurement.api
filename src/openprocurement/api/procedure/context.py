from openprocurement.api.context import get_request


def get_object(obj_name) -> dict | None:
    request = get_request()
    return request.validated.get(obj_name)


def get_plan() -> dict | None:
    return get_object("plan")


def get_tender() -> dict | None:
    return get_object("tender")


def get_contract() -> dict | None:
    return get_object("contract")


def get_framework() -> dict | None:
    return get_object("framework")


def get_submission() -> dict | None:
    return get_object("submission")


def get_qualification() -> dict | None:
    return get_object("qualification")


def get_agreement() -> dict | None:
    return get_object("agreement")
