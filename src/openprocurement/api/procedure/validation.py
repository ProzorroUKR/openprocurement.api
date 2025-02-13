from copy import deepcopy

from schematics.exceptions import ValidationError

from openprocurement.api.auth import ACCR_RESTRICTED
from openprocurement.api.constants import CPV_PREFIX_LENGTH_TO_NAME
from openprocurement.api.context import get_request
from openprocurement.api.procedure.utils import (
    apply_data_patch,
    get_cpv_prefix_length,
    get_cpv_uniq_prefixes,
    is_item_owner,
)
from openprocurement.api.utils import (
    delete_nones,
    handle_data_exceptions,
    raise_operation_error,
)
from openprocurement.api.validation import (
    validate_accreditation_level_base,
    validate_accreditation_level_mode,
    validate_json_data,
)
from openprocurement.tender.core.procedure.documents import (
    check_document,
    check_document_batch,
    update_document_url,
)


def validate_input_data(input_model, allow_bulk=False, filters=None, none_means_remove=False):
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
                # NOTE: empty list does the same for list fields
                for k, v in input_data.items():
                    if v is None or isinstance(v, list) and len(v) == 0:
                        result[k] = v
            valid_data = validate_data(request, input_model, input_data)
            if valid_data is not None:
                result.update(valid_data)
            data.append(result)

        if filters:
            data = [f(request, d) for f in filters for d in data]
        request.validated["data"] = data if allow_bulk else data[0]
        return request.validated["data"]

    return validate


def validate_data(request, model, data, to_patch=False, collect_errors=False):
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
        data = validate_data(request, input_model, data)
        request.validated["data"] = data
        return data

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


def validate_item_owner(item_name, token_field_name="owner_token"):
    def validator(request, **_):
        item = request.validated[item_name]
        if not is_item_owner(request, item, token_field_name=token_field_name):
            raise_operation_error(request, "Forbidden", location="url", name="permission")
        else:
            if item_name == "claim":
                request.authenticated_role = "complaint_owner"  # we have complaint_owner is documents.author
            else:
                request.authenticated_role = f"{item_name}_owner"

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
        data_patch = request.validated["data"]
        data_src = request.validated[item_name]

        data = apply_data_patch(data_src, data_patch)
        if data:
            data = validate_data(request, model, data)
        request.validated["data"] = data
        return data

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
                        patch.pop("status", None)  # do not change lot status by tender patch
                        lot_data.update(patch)
                    new_lots.append(lot_data)
                data["lots"] = new_lots
            elif "lots" in data:
                del data["lots"]

        data.update(patch_data)
        request.validated["data"] = validate_data(request, model, data)
        return request.validated["data"]

    return validate


def validate_config_data(default=None):
    """
    Put config in data dict
    :param default:
    :return:
    """
    default = default or {}

    def validate(request, **_):
        config = request.json.get("config") or default
        request.validated["data"]["config"] = config
        return config

    return validate


def validate_accreditation_level(levels, item, operation, source="tender", kind_central_levels=None):
    def validate(request, **kwargs):
        # operation
        validate_accreditation_level_base(request, levels, item, operation)

        # real mode acc lvl
        mode = request.validated[source].get("mode")
        validate_accreditation_level_mode(request, mode, item, operation)

        # procuringEntity.kind = central
        if kind_central_levels:
            pe = request.validated[source].get("procuringEntity")
            if pe:
                kind = pe.get("kind")
                if kind == "central":
                    validate_accreditation_level_base(request, kind_central_levels, item, operation)

    return validate


def validate_input_data_from_resolved_model(none_means_remove=False):
    def validated(request, **_):
        state = request.root.state
        method = request.method.lower()
        model = getattr(state, f"get_{method}_data_model")()
        request.validated[f"{method}_data_model"] = model
        validate = validate_input_data(model, none_means_remove=none_means_remove)
        return validate(request, **_)

    return validated


def validate_patch_data_from_resolved_model(item_name):
    def validated(request, **_):
        state = request.root.state
        model = state.get_parent_patch_data_model()
        validate = validate_patch_data(model, item_name)
        return validate(request, **_)

    return validated


def validate_values_uniq(values):
    codes = [i.get("value") for i in values]
    if any(codes.count(i) > 1 for i in set(codes)):
        raise ValidationError("Feature value should be uniq for feature")


def validate_features_uniq(features):
    if features:
        codes = [feature.get("code") for feature in features]
        if any(codes.count(i) > 1 for i in set(codes)):
            raise ValidationError("Feature code should be uniq for all features")


def validate_parameters_uniq(parameters):
    if parameters:
        codes = [param.get("code") for param in parameters]
        if [i for i in set(codes) if codes.count(i) > 1]:
            raise ValidationError("Parameter code should be uniq for all parameters")


def validate_data_documents(route_key="tender_id", uid_key="_id"):
    def validate(request, **_):
        data = request.validated["data"]
        for key in data.keys():
            if key == "documents" or "Documents" in key:
                if data[key]:
                    docs = []
                    for document in data[key]:
                        # some magic, yep
                        # route_kwargs = {"bid_id": data["id"]}
                        route_kwargs = {route_key: data[uid_key]}
                        document = check_document_batch(request, document, key, route_kwargs)
                        docs.append(document)

                    # replacing documents in request.validated["data"]
                    if docs:
                        data[key] = docs
        return data

    return validate


def validate_upload_document(request, **_):
    document = request.validated["data"]
    delete_nones(document)

    # validating and uploading magic
    check_document(request, document)
    document_route = request.matched_route.name.replace("collection_", "")
    update_document_url(request, document, document_route, {})


def update_doc_fields_on_put_document(request, **_):
    """
    PUT document means that we upload a new version, but some of the fields is taken from the base version
    we have to copy these fields in this method and insert before document model validator
    """
    document = request.validated["data"]
    prev_version = request.validated["document"]
    json_data = request.validated["json_data"]

    # here we update new document with fields from the previous version
    force_replace = ("id", "author", "format", "documentType")
    black_list = ("title", "url", "datePublished", "dateModified", "hash")
    for key, value in prev_version.items():
        if key in force_replace or (key not in black_list and key not in json_data):
            document[key] = value


def validate_restricted_object_action(request, obj_name, obj):
    if request.method in ("GET", "HEAD"):
        # Skip validation.
        # Data will be masked for requests with no access to restricted object
        return

    if all(
        [
            obj["config"].get("restricted", False) is False,
            obj["config"].get("restrictedDerivatives", False) is False,
        ]
    ):
        # Skip validation.
        # It's not a restricted object
        return

    if request.authenticated_role != "brokers":
        # Skip validation.
        # Only brokers can have restrictions on access to restricted objects
        return

    validate_accreditation_level_base(
        request,
        (ACCR_RESTRICTED,),
        obj_name,
        "restricted data access",
    )


def validate_classifications_prefixes(
    classifications,
    root_classification=None,
    root_name="root",
):
    """
    Validate that all CPV codes have the same prefix

    For example, if we have a root classification with CPV code 12340000-9
    and items with CPV codes 12341111-9 and 12342222-9:
       - the prefix length is 4
       - prefix name is 'class'
       - the actual prefixes to compare are 1234, 1234, 1234 (validation error will not be raised)
    """
    if root_classification:
        classifications.append(root_classification)
    prefix_length = get_cpv_prefix_length(classifications)
    prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
    error_message = f"CPV {prefix_name} of items should be identical"
    if root_classification:
        error_message += f" to {root_name} cpv"
    if len(get_cpv_uniq_prefixes(classifications, prefix_length)) != 1:
        raise_operation_error(
            get_request(),
            [error_message],
            status=422,
            name="items",
        )
