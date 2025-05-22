from schematics.exceptions import ValidationError
from simplejson import JSONDecodeError

from openprocurement.api.auth import ACCR_EXIT, ACCR_TEST, check_user_accreditations
from openprocurement.api.utils import (
    error_handler,
    get_first_revision_date,
    get_now,
    raise_operation_error,
)

OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update", "DELETE": "delete"}


def validate_json_data(request, allow_bulk=False, **kwargs):
    try:
        json = request.json
    except JSONDecodeError as e:
        request.errors.add("body", "data", str(e))
        # request.errors.add("body", "data", "No JSON object could be decoded")  # Expecting value: line 1 column 1 (char 0)
        request.errors.status = 422
        raise error_handler(request)
    data = json.get("data") if isinstance(json, dict) else None
    allowed_types = (list, dict) if allow_bulk else dict
    if any(
        [
            not isinstance(data, allowed_types),
            isinstance(data, list) and not data,
            isinstance(data, list) and not all(isinstance(i, dict) for i in data),
        ]
    ):
        request.errors.add("body", "data", "Data not available")
        request.errors.status = 422
        raise error_handler(request)
    request.validated["json_data"] = data
    return data


def validate_items_uniq(items, *args):
    if items:
        ids = [i.id for i in items]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError("Item id should be uniq for all items")


def validate_accreditation_level_base(request, levels, name, action):
    if not request.check_accreditations(levels):
        request.errors.add(
            "url",
            "accreditation",
            "Broker Accreditation level does not permit {} {}".format(name, action),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_accreditation_level_mode(request, mode, name, action):
    if mode is None and request.check_accreditations((ACCR_TEST,)):
        request.errors.add(
            "url",
            "mode",
            "Broker Accreditation level does not permit {} {}".format(name, action),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_accreditation_level_owner(request, owner, location, name, action):
    if not check_user_accreditations(request, owner, (ACCR_EXIT,), default=True):
        request.errors.add(
            "url",
            "accreditation",
            "Owner Accreditation level does not permit {} {}".format(name, action),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_tender_first_revision_date(request, validation_date, message="Forbidden"):
    tender = request.validated["tender"]
    tender_creation_date = get_first_revision_date(tender, default=get_now())
    if tender_creation_date < validation_date:
        raise_operation_error(request, message)
