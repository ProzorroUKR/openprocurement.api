from copy import deepcopy

from openprocurement.api.utils import handle_data_exceptions, raise_operation_error
from openprocurement.api.validation import (
    validate_json_data,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
)
from openprocurement.api.procedure.utils import is_item_owner, apply_data_patch


def validate_input_data(input_model, allow_bulk=False, filters=None, none_means_remove=False, whitelist=None):
    """
    :param input_model: a model to validate data against
    :param allow_bulk: if True, request.validated["data"] will be a list of valid inputs
    :param filters: list of filter function that applied on valid data
    :param none_means_remove: null values passed cause deleting saved values at those keys
    :return:
    """
    def validate(request, **_):
        request.validated["json_data"] = json_data = validate_json_data(request, allow_bulk=allow_bulk)
        # now you can use context.get_json_data() in model validators to access the whole passed object
        # instead of .__parent__.__parent__. Though it may not be valid
        if not isinstance(json_data, list):
            json_data = [json_data]

        data = []
        for input_data in json_data:
            result = {}
            if none_means_remove:
                # if None is passed it should be added to the result
                # None means that the field value is deleted
                # IMPORTANT: input_data can contain more fields than are allowed to update
                # validate_data will raise Rogue field error then
                # Update: doesn't work with sub-models {'auctionPeriod': {'startDate': None}}
                for k, v in input_data.items():
                    if (
                            v is None
                            or isinstance(v, list) and len(v) == 0  # for list fields, an empty list does the same
                    ):
                        result[k] = v
            # TODO: Remove it
            if whitelist:
                filter_whitelist(input_data, whitelist)
            valid_data = validate_data(request, input_model, input_data)
            if valid_data is not None:
                result.update(valid_data)
            data.append(result)

        if filters:
            data = [f(request, d) for f in filters for d in data]
        request.validated["data"] = data if allow_bulk else data[0]
        return request.validated["data"]

    return validate


def validate_data(request, model, data, to_patch=False):
    with handle_data_exceptions(request):
        instance = model(data)
        instance.validate()
        data = instance.serialize()
    return data


def validate_data_model(input_model):
    """
    Simple way to validate data in request.validated["data"] against a provided model
    the result is put back in request.validated["data"]
    :param input_model:
    :return:
    """
    def validate(request, **_):
        data = request.validated["data"]
        request.validated["data"] = validate_data(request, input_model, data)
        return request.validated["data"]
    return validate


def filter_whitelist(data: dict, filter_data: dict) -> None:
    new_data = filter_dict(data, filter_data)
    for field in new_data:
        data[field] = new_data[field]


def filter_dict(data: dict, filter_data: dict):
    new_data = {}
    for field in filter_data:
        if field not in data:
            continue
        elif isinstance(filter_data[field], set):
            new_data[field] = {k: v for k, v in data[field].items() if k in filter_data[field]}
        elif isinstance(filter_data[field], list):
            new_data[field] = filter_list(data[field], filter_data[field][0])
        elif isinstance(filter_data[field], dict):
            new_data[field] = filter_dict(data[field], filter_data[field])
        else:
            new_data[field] = data[field]
    return new_data


def filter_list(input: list, filters: dict) -> list:
    new_items = []
    for item in input:
        new_items.append(filter_dict(item, filters))
    return new_items


def unless_administrator(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "Administrator":
            for validation in validations:
                validation(request)
    return decorated


def unless_admins(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "admins":
            for validation in validations:
                validation(request)
    return decorated


def unless_bots(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "bots":
            for validation in validations:
                validation(request)
    return decorated


def unless_item_owner(*validations, item_name):
    def decorated(request, **_):
        item = request.validated[item_name]
        if not is_item_owner(request, item):
            for validation in validations:
                validation(request)
    return decorated


def unless_bots_or_auction(*validations):
    def decorated(request, **_):
        if request.authenticated_role not in ("bots", "auction"):
            for validation in validations:
                validation(request)
    return decorated


def validate_item_owner(item_name):
    def validator(request, **_):
        item = request.validated[item_name]
        if not is_item_owner(request, item):
            raise_operation_error(
                request,
                "Forbidden",
                location="url",
                name="permission"
            )
    return validator


def validate_patch_data(model, item_name):
    """
    Because api supports questionable requests like
    PATCH /bids/uid {"parameters": [{}, {}, {"code": "new_code"}]}
    where {}, {} and {"code": "new_code"} are invalid parameters and can't be validated.
    We have to have this validator that
    1) Validate requests data against simple patch model
    (use validator validate_input_data(PatchModel) before this one)
    2) Apply the patch on the saved data  (covered by this validator)
    3) Validate patched data against the full model (covered by this validator)
    In fact, the output of the second model is what should be sent to the api, to make everything simple
    :param model:
    :param item_name:
    :return:
    """
    def validate(request, **_):
        patch_data = request.validated["data"]
        request.validated["data"] = data = apply_data_patch(request.validated[item_name], patch_data)
        if data:
            request.validated["data"] = validate_data(request, model, data)
        return request.validated["data"]
    return validate


def validate_patch_data_simple(model, item_name):
    """
    Does same thing as validate_patch_data
    but doesn't apply data recursively
    :param model:
    :param item_name:
    :return:
    """
    def validate(request, **_):
        patch_data = request.validated["data"]
        data = deepcopy(request.validated[item_name])

        # check if there are any changes
        for f, v in patch_data.items():
            if data.get(f) != v:
                break
        else:
            request.validated["data"] = {}
            return  # no changes

        # TODO: move lots management to a distinct endpoint!
        if "lots" in patch_data:
            patch_lots = patch_data.pop("lots", None)
            if patch_lots:
                new_lots = []
                for patch, lot_data in zip(patch_lots, data["lots"]):
                    # if patch_lots is shorter, then some lots are going to be deleted
                    # longer, then some lots are going to be added
                    if lot_data is None:
                        lot_data = patch  # new lot
                    else:
                        lot_data.update(patch)
                    new_lots.append(lot_data)
                data["lots"] = new_lots
            elif "lots" in data:
                del data["lots"]

        data.update(patch_data)
        request.validated["data"] = validate_data(request, model, data)
        return request.validated["data"]
    return validate


def validate_accreditation_level(levels, item, operation, source="tender", kind_central_levels=None):
    def validate(request, **kwargs):
        # operation
        _validate_accreditation_level(request, levels, item, operation)

        # real mode acc lvl
        mode = request.validated[source].get("mode")
        _validate_accreditation_level_mode(request, mode, item, operation)

        # procuringEntity.kind = central
        if kind_central_levels:
            pe = request.validated[source].get("procuringEntity")
            if pe:
                kind = pe.get("kind")
                if kind == "central":
                    _validate_accreditation_level(request, kind_central_levels, item, operation)
    return validate


def validate_input_data_from_resolved_model():
    def validated(request, **_):
        state = request.root.state
        method = request.method.lower()
        model = getattr(state, f"get_{method}_data_model")()
        request.validated[f"{method}_data_model"] = model
        validate = validate_input_data(model)
        return validate(request, **_)
    return validated


def validate_patch_data_from_resolved_model(item_name):
    def validated(request, **_):
        state = request.root.state
        model = state.get_parent_patch_data_model()
        validate = validate_patch_data(model, item_name)
        return validate(request, **_)
    return validated
