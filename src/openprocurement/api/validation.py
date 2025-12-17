from schematics.exceptions import ValidationError
from simplejson import JSONDecodeError

from openprocurement.api.auth import AccreditationPermission, check_user_accreditations
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
    validation_func = validate_list_uniq_factory("Item id should be uniq for all items", "id")
    validation_func(items)


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
    if mode is None and request.check_accreditations((AccreditationPermission.ACCR_TEST,)):
        request.errors.add(
            "url",
            "mode",
            "Broker Accreditation level does not permit {} {}".format(name, action),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_accreditation_level_owner(request, owner, location, name, action):
    if not check_user_accreditations(request, owner, (AccreditationPermission.ACCR_EXIT,), default=True):
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


def validate_list_uniq_factory(err_msg, field_attrs=()):
    """
    Factory for ListType validators that require unique items
    """
    if not isinstance(field_attrs, (list, tuple, set, frozenset)):
        field_attrs = (field_attrs,)

    def _get_attr(item, field_attr):
        """
        Function gets nested attribute of the provided item
        """
        for x in field_attr.split("."):
            item = item.get(x, {})
        return item

    def _validate_uniq(values, *args, **kwargs):
        """
        Main validator function
        """
        if values:
            res = values
            # if item attributes were provided get unique identifier by using provided attributes
            if field_attrs:
                res = [tuple(_get_attr(x, a) for a in field_attrs) for x in res]
            if len(res) > len(set(res)):
                raise ValidationError(err_msg)

    return _validate_uniq
