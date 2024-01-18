from typing import Union

from openprocurement.api.context import get_request


def get_object(obj_name) -> Union[dict, None]:
    request = get_request()
    return request.validated.get(obj_name)


def get_object_config(obj_name) -> Union[dict, None]:
    obj = get_object(obj_name)
    if not obj:
        return
    return obj.get("config")


def get_plan() -> Union[dict, None]:
    return get_object("plan")


def get_tender() -> Union[dict, None]:
    return get_object("tender")


def get_tender_config() -> Union[dict, None]:
    return get_object_config("tender")


def get_contract() -> Union[dict, None]:
    return get_object("contract")


def get_contract_config() -> Union[dict, None]:
    return get_object_config("contract")


def get_framework() -> Union[dict, None]:
    return get_object("framework")


def get_submission() -> Union[dict, None]:
    return get_object("submission")


def get_qualification() -> Union[dict, None]:
    return get_object("qualification")


def get_agreement() -> Union[dict, None]:
    return get_object("agreement")
