from iso8601 import parse_date

from pyramid.request import Request

from openprocurement.api.constants import (
    RELEASE_2020_04_19,
    CRITERION_REQUIREMENT_STATUSES_FROM,
    RELEASE_GUARANTEE_CRITERION_FROM,
    GUARANTEE_ALLOWED_TENDER_TYPES,
    RELEASE_ECRITERIA_ARTICLE_17,
)
from openprocurement.api.utils import (
    to_decimal,
    raise_operation_error,
    handle_data_exceptions,
    error_handler,
)
from openprocurement.api.validation import (
    validate_json_data,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
    _validate_tender_first_revision_date,
    OPERATIONS,
)
from openprocurement.tender.core.validation import TYPEMAP
from openprocurement.tender.core.constants import AMOUNT_NET_COEF
from openprocurement.tender.core.procedure.utils import (
    is_item_owner,
    apply_data_patch,
    delete_nones,
    get_first_revision_date,
    get_contracts_values_related_to_patched_contract,
    find_item_by_id,
)
from openprocurement.tender.core.utils import calculate_tender_business_date, find_lot
from openprocurement.tender.core.procedure.documents import check_document_batch, check_document, update_document_url
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import get_criterion_requirement
from schematics.exceptions import ValidationError
from pyramid.httpexceptions import HTTPError
from copy import deepcopy
from schematics.types import BaseType
from decimal import Decimal, ROUND_UP
import logging


LOGGER = logging.getLogger(__name__)
OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update", "DELETE": "delete"}


def filter_list(input: list, filters: dict) -> list:
    new_items = []
    for item in input:
        new_items.append(filter_dict(item, filters))
    return new_items


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


def filter_whitelist(data: dict, filter_data: dict) -> None:
    new_data = filter_dict(data, filter_data)
    for field in new_data:
        data[field] = new_data[field]


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


def validate_config_data(input_model, obj_name=None, default=None):
    """
    Simple way to validate config in request.validated["config"] against a provided model
    the result is put back in request.validated["config"]
    :param input_model:
    :param obj_name:
    :param default:
    :return:
    """
    default = default or {}
    def validate(request, **_):
        config_name = f"{obj_name}_config" if obj_name else "config"
        config = request.json.get("config") or default
        request.validated[config_name] = validate_data(request, input_model, config) or {}
        return request.validated[config_name]
    return validate


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


def validate_item_operation_in_disallowed_tender_statuses(item_name, allowed_statuses):
    """
    Factory disallowed any operation in specified statuses
    :param item_name: str
    :param not_allowed_statuses: list
    :return:
    """
    def validate(request, **_):
        tender = request.validated["tender"]
        if tender["status"] not in allowed_statuses:
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} {item_name} in current ({tender['status']}) tender status",
            )
    return validate


def validate_data(request, model, data, to_patch=False, collect_errors=False):
    with handle_data_exceptions(request):
        instance = model(data)
        instance.validate()
        data = instance.serialize()
    return data


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


def validate_contract_supplier():
    def validator(request, **_):
        contract = request.validated["contract"]
        tender = request.validated["tender"]
        award = find_item_by_id(tender["awards"], contract["awardID"])
        bid = find_item_by_id(tender["bids"], award.get("bid_id"))

        if is_item_owner(request, bid):
            request.authenticated_role = "contract_supplier"
        elif is_item_owner(request, tender):
            request.authenticated_role = "tender_owner"
        else:
            raise_operation_error(
                request,
                "Forbidden",
                location="url",
                name="permission"
            )
    return validator


def unless_item_owner(*validations, item_name):
    def decorated(request, **_):
        item = request.validated[item_name]
        if not is_item_owner(request, item):
            for validation in validations:
                validation(request)
    return decorated


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


def unless_bots_or_auction(*validations):
    def decorated(request, **_):
        if request.authenticated_role not in ("bots", "auction"):
            for validation in validations:
                validation(request)
    return decorated


def validate_any(*validations):
    """
    use case:
    @json_view(
        validators=(
            validate_any(
                validate_item_owner("tender"),
                validate_item_owner("bid"),
            ),
            ...
        ),
        ...
    )
    :param validations:
    :return:
    """
    def decorated(request, **_):
        e = AssertionError("validations list can't be empty")
        errors_on_start = deepcopy(request.errors)
        for validation in validations:
            try:
                validation(request)
            except HTTPError as e:
                pass
            else:  # on success
                request.errors = errors_on_start
                break
        else:
            raise e
    return decorated


def validate_accreditation_level(levels, item, operation, source="tender", kind_central_levels=None):
    def validate(request, **_):
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


def validate_bid_accreditation_level(request, **kwargs):  # TODO: use validate_accreditation_level directly
    validator = validate_accreditation_level(request.tender_model.edit_accreditations, "bid", "creation")
    validator(request, **kwargs)


def validate_operation_in_tender_statuses(obj_name, valid_statuses=None, not_valid_statuses=None):
    if valid_statuses and not_valid_statuses:
        raise ValueError("should be defined only one of two values(valid_statuses or not_valid_statuses)")

    def wrapper(request, **__):
        tender_status = request.validated["tender"]["status"]
        if (
            (valid_statuses and tender_status not in valid_statuses)
            or (not_valid_statuses and tender_status in not_valid_statuses)
        ):
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} {obj_name.lower()} in current ({tender_status}) tender status",
            )
    return wrapper


# bids
def validate_bid_operation_period(request, **_):
    tender = request.validated["tender"]
    tender_period = tender.get("tenderPeriod", {})
    if (
        tender_period.get("startDate")
        and get_now().isoformat() < tender_period.get("startDate")
        or get_now().isoformat() > tender_period.get("endDate", "")  # TODO: may "endDate" be missed ?
    ):
        operation = "added" if request.method == "POST" else "deleted"
        if request.authenticated_role != "Administrator" and request.method in ("PUT", "PATCH"):
            operation = "updated"
        raise_operation_error(
            request,
            "Bid can be {} only during the tendering period: from ({}) to ({}).".format(
                operation,
                tender_period.get("startDate"),
                tender_period.get("endDate"),
            ),
        )


def validate_bid_operation_in_tendering(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status == "active.tendering":
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", tender_status
            ),
        )


def validate_bid_operation_not_in_tendering(request, **_):
    status = request.validated["tender"]["status"]
    if status != "active.tendering":
        operation = "add" if request.method == "POST" else "delete"
        if request.authenticated_role != "Administrator" and request.method in ("PUT", "PATCH"):
            operation = "update"
        raise_operation_error(
            request, "Can't {} bid in current ({}) tender status".format(operation, status)
        )


def validate_lotvalue_value(tender, related_lot, value):
    lot = find_lot(tender, related_lot)
    if lot and value:
        tender_lot_value = lot.get("value")
        validate_lot_value_amount(tender_lot_value, value)
        validate_lot_value_currency(tender_lot_value, value)
        validate_lot_value_vat(tender_lot_value, value)


def validate_lot_value_amount(tender_lot_value, value):
    if float(tender_lot_value["amount"]) < value.amount:
        raise ValidationError("value of bid should be less than value of lot")


def validate_lot_value_currency(tender_lot_value, value):
    if tender_lot_value["currency"] != value.currency:
        raise ValidationError("currency of bid should be identical to currency of value of lot")


def validate_lot_value_vat(tender_lot_value, value):
    if tender_lot_value["valueAddedTaxIncluded"] != value.valueAddedTaxIncluded:
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
        )


def validate_bid_value(tender, value):
    if tender.get("lots"):
        if value:
            raise ValidationError("value should be posted for each lot of bid")
    else:
        tender_value = tender.get("value")
        if not value:
            raise ValidationError("This field is required.")
        if to_decimal(tender_value["amount"]) < to_decimal(value.amount):
            raise ValidationError("value of bid should be less than value of tender")
        if tender_value["currency"] != value.currency:
            raise ValidationError("currency of bid should be identical to currency of value of tender")
        if tender_value["valueAddedTaxIncluded"] != value.valueAddedTaxIncluded:
            raise ValidationError(
                "valueAddedTaxIncluded of bid should be identical " "to valueAddedTaxIncluded of value of tender"
            )


def validate_value_type(value, datatype):
    if not value:
        return
    type_ = TYPEMAP.get(datatype)
    if not type_:
        raise ValidationError(
            'Type mismatch: value {} does not confront type {}'.format(
                value, type_
            )
        )
    # validate value
    return type_.to_native(value)


def validate_related_lot(tender, related_lot):
    if related_lot not in [lot["id"] for lot in tender.get("lots") or [] if lot]:
        raise ValidationError("relatedLot should be one of lots")


def validate_view_bid_document(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status in ("active.tendering", "active.auction") \
       and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_view_bids(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status in ("active.tendering", "active.auction"):
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", tender_status
            ),
        )


def validate_update_deleted_bid(request, **_):
    if request.validated["bid"]["status"] == "deleted":
        raise_operation_error(request, "Can't update bid in (deleted) status")


def validate_bid_document_operation_period(request, **_):
    tender = request.validated["tender"]
    now = get_now().isoformat()
    if tender["status"] == "active.tendering":
        tender_period = tender["tenderPeriod"]
        if (
            tender_period.get("startDate") and now < tender_period["startDate"]
            or now > tender_period["endDate"]
        ):
            raise_operation_error(
                request,
                "Document can be {} only during the tendering period: from ({}) to ({}).".format(
                    "added" if request.method == "POST" else "updated",
                    tender_period.get("startDate"),
                    tender_period["endDate"],
                ),
            )


# bids req response
def base_validate_operation_ecriteria_objects(request, valid_statuses="", obj_name="tender"):
    _validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    current_status = request.validated[obj_name]["status"]
    if current_status not in valid_statuses:
        raise_operation_error(request, "Can't {} object if {} not in {} statuses".format(
            request.method.lower(), obj_name, valid_statuses))


def validate_operation_ecriteria_on_tender_status(request, **_):
    valid_statuses = ["draft", "draft.pending", "draft.stage2", "active.tendering"]
    base_validate_operation_ecriteria_objects(request, valid_statuses)


def validate_operation_award_requirement_response(request, **kwargs):
    _validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    valid_tender_statuses = ["active.qualification"]
    base_validate_operation_ecriteria_objects(request, valid_tender_statuses)


def validate_view_requirement_responses(request, **_):
    pre_qualification_tenders = ["aboveThresholdEU", "competitiveDialogueUA",
                                 "competitiveDialogueEU", "competitiveDialogueEU.stage2",
                                 "esco", "closeFrameworkAgreementUA"]

    tender_type = request.validated["tender"]["procurementMethodType"]
    if tender_type in pre_qualification_tenders:
        invalid_tender_statuses = ["active.tendering"]
    else:
        invalid_tender_statuses = ["active.tendering", "active.auction"]

    tender_status = request.validated["tender"]["status"]
    if tender_status in invalid_tender_statuses:

        raise_operation_error(
            request,
            f"Can't view {'bid' if request.matchdict.get('bid_id') else 'bids'} "
            f"in current ({tender_status}) tender status"
        )


# qualification req response
def validate_operation_qualification_requirement_response(request, **_):
    _validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    base_validate_operation_ecriteria_objects(request, ["pending"], "qualification")


# bid req response evidence
def validate_operation_ecriteria_objects_evidences(request, **_):
    valid_statuses = ["draft", "draft.pending", "draft.stage2", "active.tendering"]

    tender = request.validated["tender"]
    requirement_id = request.validated["requirement_response"]["requirement"]["id"]
    criterion = get_criterion_requirement(tender, requirement_id)
    guarantee_criterion = "CRITERION.OTHER.CONTRACT.GUARANTEE"

    if criterion and criterion["classification"]["id"].startswith(guarantee_criterion):
        awarded_status = ["active.awarded", "active.qualification"]
        valid_statuses.extend(awarded_status)
        if tender["status"] not in awarded_status:
            raise_operation_error(request, f"available only in {awarded_status} statuses")

        bid_id = request.validated["bid"]["id"]
        active_award = None
        for award in tender.get("awards", ""):
            if award["status"] == "active" and award["bid_id"] == bid_id:
                active_award = award
                break

        if active_award is None:
            raise_operation_error(request, f"{guarantee_criterion} available only with active award")

        current_contract = None
        for contract in tender.get("contracts", ""):
            if contract.get("awardId") == active_award["id"]:
                current_contract = contract
                break
        if current_contract and current_contract.status == "pending":
            raise_operation_error(request, "forbidden if contract not in status `pending`")

    base_validate_operation_ecriteria_objects(request, valid_statuses)


# documents
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
    force_replace = ("id", "author", "datePublished")
    black_list = ("title", "format", "url", "dateModified", "hash")
    for key, value in prev_version.items():
        if key in force_replace or (key not in black_list and key not in json_data):
            document[key] = value


# for openua, openeu
def unless_allowed_by_qualification_milestone(*validations):
    """
    decorator for 24hours and anomaly low price features to skip some view validator functions
    :param validation: a function runs unless it's disabled by an active qualification milestone
    :return:
    """
    def decorated_validation(request, **_):
        now = get_now().isoformat()
        tender = request.validated["tender"]
        bid_id = request.validated["bid"]["id"]
        awards = [q for q in tender.get("awards", "")
                  if q["status"] == "pending" and q["bid_id"] == bid_id]

        # 24 hours
        if "qualifications" in tender:   # for procedures with pre-qualification
            qualifications = [q for q in tender["qualifications"]
                              if q["status"] == "pending" and q["bidID"] == bid_id]
        else:
            qualifications = awards

        for q in qualifications:
            for milestone in q.get("milestones", ""):
                if milestone["code"] == "24h" and milestone["date"] <= now <= milestone["dueDate"]:
                    return  # skipping the validation because of 24 hour milestone

        # low price
        for award in awards:
            for milestone in award.get("milestones", ""):
                if milestone["date"] <= now <= milestone["dueDate"]:
                    if milestone["code"] == "alp":
                        return  # skipping the validation because of low price milestone

        # else
        for validation in validations:
            validation(request)

    return decorated_validation


# auction
def validate_auction_tender_status(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status != "active.auction":
        operations = {
            "GET": "get auction info",
            "POST": "report auction results",
            "PATCH": "update auction urls",
        }
        raise_operation_error(
            request, f"Can't {operations[request.method]} in current ({tender_status}) tender status"
        )


def validate_auction_tender_non_lot(request, **_):
    tender = request.validated["tender"]
    if tender.get("lots"):
        raise_operation_error(
            request,
            [{"participationUrl": ["url should be posted for each lot of bid"]}],
            location="body", name="bids",
            status=422,
        )


def validate_active_lot(request, **_):
    tender = request.validated["tender"]
    lot_id = request.matchdict.get("auction_lot_id")
    if not any(
        lot["status"] == "active"
        for lot in tender.get("lots", "")
        if lot["id"] == lot_id
    ):
        raise_operation_error(
            request,
            "Can {} only in active lot status".format(
                "report auction results" if request.method == "POST" else "update auction urls"
            ),
        )


# award
def validate_create_award_not_in_allowed_period(request, **_):
    tender = request.validated["tender"]
    if tender["status"] != "active.qualification":
        raise_operation_error(request, f"Can't create award in current ({tender['status']}) tender status")


def validate_create_award_only_for_active_lot(request, **_):
    tender = request.validated["tender"]
    award = request.validated["data"]
    if any(lot.get("status") != "active" for lot in tender.get("lots", "")
           if lot["id"] == award.get("lotID")):
        raise_operation_error(request, "Can create award only in active lot status")


def validate_update_award_in_not_allowed_status(request, **_):
    tender = request.validated["tender"]
    if tender["status"] not in ("active.qualification", "active.awarded"):
        raise_operation_error(request, f"Can't update award in current ({tender['status']}) tender status")


def validate_update_award_only_for_active_lots(request, **_):
    tender = request.validated["tender"]
    award = request.validated["award"]
    if any(lot.get("status") != "active" for lot in tender.get("lots", "")
           if lot.get("id") == award.get("lotID")):
        raise_operation_error(request, "Can update award only in active lot status")


def validate_award_with_lot_cancellation_in_pending(request, **_):
    if request.authenticated_role != "tender_owner":
        return

    tender = get_tender()
    lot_id = request.validated["award"].get("lotID")
    if not lot_id:
        return

    tender_created = get_first_revision_date(tender, default=get_now())
    if tender_created < RELEASE_2020_04_19:
        return

    accept_lot = all(
        any(
            complaint.get("status") == "resolved"
            for complaint in cancellation["complaints"]
        )
        for cancellation in tender.get("cancellations", [])
        if cancellation.get("status") == "unsuccessful"
        and cancellation.get("complaints")
        and cancellation.get("relatedLot") == lot_id
    )
    has_lot_pending_cancellations = any(
        cancellation.get("relatedLot") == lot_id
        and cancellation.get("status") == "pending"
        for cancellation in tender.get("cancellations", [])
    )
    if (
        has_lot_pending_cancellations
        or not accept_lot
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} award with lot that have active cancellation",
        )


def validate_update_award_with_accepted_complaint(request, **_):
    tender = get_tender()
    lot_id = request.validated["award"].get("lotID")
    if any(
        any(c.get("status") == "accepted"
            for c in i.get("complaints", ""))
        for i in tender.get("awards", "")
        if i.get("lotID") == lot_id
    ):
        raise_operation_error(request, "Can't update award with accepted complaint")


def validate_update_award_status_before_milestone_due_date(request, **_):
    from openprocurement.tender.core.models import QualificationMilestone
    award = request.validated["award"]
    sent_status = request.json.get("data", {}).get("status")
    if award.get("status") == "pending" and sent_status != "pending":
        now = get_now().isoformat()
        for milestone in award.get("milestones", ""):
            if (
                milestone["code"] in (QualificationMilestone.CODE_24_HOURS, QualificationMilestone.CODE_LOW_PRICE)
                and milestone["date"] <= now <= milestone["dueDate"]
            ):
                raise_operation_error(
                    request,
                    f"Can't change status to '{sent_status}' until milestone.dueDate: {milestone['dueDate']}"
                )


# AWARD DOCUMENTS
def validate_award_document_tender_not_in_allowed_status_base(
    request, allowed_bot_statuses=("active.awarded",), **_
):
    allowed_tender_statuses = ["active.qualification"]
    if request.authenticated_role == "bots":
        allowed_tender_statuses.extend(allowed_bot_statuses)
    status = request.validated["tender"]["status"]
    if status not in allowed_tender_statuses:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({status}) tender status"
        )


def validate_award_document_lot_not_in_allowed_status(request, **_):
    award_lot_id = request.validated["award"].get("lotID")
    if any(
        i.get("status", "active") != "active"
        for i in request.validated["tender"].get("lots", "")
        if i["id"] == award_lot_id
    ):
        raise_operation_error(request, f"Can {OPERATIONS.get(request.method)} document only in active lot status")


def get_award_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


def validate_award_document_author(request, **_):
    doc_author = request.validated["document"].get("author") or "tender_owner"
    role = get_award_document_role(request)
    if doc_author == "bots" and role != "bots":
    # if role != doc_author:   # TODO: unkoment when "author": "brokers" fixed
        raise_operation_error(
            request,
            "Can update document only author",
            location="url",
            name="role",
        )


# TENDER
def validate_tender_status_allows_update(*statuses):
    def validate(request, **_):
        tender_status = get_tender()["status"]
        if tender_status not in statuses:
            raise_operation_error(request, f"Can't update tender in current ({tender_status}) status")
    return validate


def validate_item_quantity(request, **_):
    items = request.validated["data"].get("items", [])
    for item in items:
        if item.get("quantity") is not None and not item["quantity"]:
            tender = get_tender()
            tender_creation_date = get_first_revision_date(tender, default=get_now())
            if tender_creation_date >= CRITERION_REQUIREMENT_STATUSES_FROM:
                related_criteria = any(
                    criterion.get("relatedItem") == item['id'] and requirement.get("status") == "active"
                    for criterion in tender.get("criteria", "")
                    for rg in criterion.get("requirementGroups", "")
                    for requirement in rg.get("requirements", "")
                )
                if related_criteria:
                    raise_operation_error(
                        request,
                        f"Can't set to 0 quantity of {item['id']} item while related criterion has active requirements"
                    )


def validate_tender_guarantee(request, **_):
    tender = request.validated["tender"]
    data = request.validated["data"]
    tender_type = tender["procurementMethodType"]
    tender_created = get_first_revision_date(tender, default=get_now())
    if (
        tender_created < RELEASE_GUARANTEE_CRITERION_FROM
        or tender_type not in GUARANTEE_ALLOWED_TENDER_TYPES
        or tender["status"] == data.get("status")
        or data.get("status") not in ("active", "active.tendering")
    ):
        return

    if tender.get("lots"):
        related_guarantee_lots = [
            criterion.get("relatedItem")
            for criterion in tender.get("criteria", "")
            if criterion.get("relatesTo") == "lot"
            and criterion.get("classification")
            and criterion["classification"]["id"] == "CRITERION.OTHER.BID.GUARANTEE"
        ]
        for lot in tender["lots"]:
            if lot["id"] in related_guarantee_lots and (
                not lot.get("guarantee") or lot["guarantee"]["amount"] <= 0
            ):
                raise_operation_error(
                    request,
                    "Should be specified 'guarantee.amount' more than 0 to lot"
                )

    else:
        amount = data["guarantee"]["amount"] if data.get("guarantee") else 0
        needed_criterion = "CRITERION.OTHER.BID.GUARANTEE"
        tender_criteria = [
            criterion["classification"]["id"]
            for criterion in tender.get("criteria", "")
            if criterion.get("classification")
        ]
        if (
            (amount <= 0 and needed_criterion in tender_criteria)
            or (amount > 0 and needed_criterion not in tender_criteria)
        ):
            raise_operation_error(
                request,
                "Should be specified {} and 'guarantee.amount' more than 0".format(needed_criterion)
            )


def validate_tender_change_status_with_cancellation_lot_pending(request, **_):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    data = request.validated["data"]
    new_status = data.get("status", tender["status"])

    if (
        tender_created < RELEASE_2020_04_19
        or not tender.get("lots")
        or tender["status"] == new_status
    ):
        return

    accept_lot = all(
        any(j.get("status") == "resolved" for j in i.get("complaints", ""))
        for i in tender.get("cancellations", "")
        if i.get("status") == "unsuccessful" and i.get("complaints") and i.get("relatedLot")
    )
    if (
        any(i.get("relatedLot") and i.get("status") == "pending" for i in tender.get("cancellations", ""))
        or not accept_lot

    ):
        raise_operation_error(
            request,
            "Can't update tender with pending cancellation in one of exists lot",
        )


# tender documents
def validate_document_operation_in_not_allowed_period(request, **_):
    tender_status = request.validated["tender"]["status"]
    if (
        request.authenticated_role != "auction" and tender_status not in (
            "active.tendering", "draft", "draft.stage2")
        or request.authenticated_role == "auction" and tender_status not in ("active.auction", "active.qualification")
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({tender_status}) tender status",
        )


def get_tender_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


def validate_tender_document_update_not_by_author_or_tender_owner(request, **_):
    document = request.validated["document"]
    role = get_tender_document_role(request)
    if role != (document.get("author") or "tender_owner"):
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request)


# QUALIFICATION
def validate_qualification_update_not_in_pre_qualification(request, **_):
    status = request.validated['tender']["status"]
    if status not in ["active.pre-qualification"]:
        raise_operation_error(request, f"Can't update qualification in current ({status}) tender status")


def validate_cancelled_qualification_update(request, **_):
    status = request.validated['qualification']["status"]
    if status == "cancelled":
        raise_operation_error(request, "Can't update qualification in current cancelled qualification status")


def validate_update_status_before_milestone_due_date(request, **_):
    from openprocurement.tender.core.procedure.models.milestone import QualificationMilestone
    qualification = request.validated['qualification']
    sent_status = request.validated["data"].get("status")
    if qualification.get('status') == "pending" and qualification.get('status') != sent_status:
        now = get_now().isoformat()
        for milestone in qualification.get('milestones', []):
            if (
                milestone["code"] in (QualificationMilestone.CODE_24_HOURS, QualificationMilestone.CODE_LOW_PRICE)
                and milestone["date"] <= now <= milestone["dueDate"]
            ):
                raise_operation_error(
                    request,
                    f"Can't change status to '{sent_status}' until milestone.dueDate: {milestone['dueDate']}"
                )


# QUALIFICATION DOCUMENT
def get_qualification_document_role(request):
    tender = request.validated["tender"]
    if is_item_owner(request, tender):
        role = "tender_owner"
    else:
        role = request.authenticated_role
    return role


def validate_qualification_update_with_cancellation_lot_pending(request, **kwargs):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    qualification = request.validated["qualification"]
    lot_id = qualification.get("lotID")

    if tender_created < RELEASE_2020_04_19 or not lot_id:
        return

    accept_lot = all([
        any([j["status"] == "resolved" for j in i["complaints"]])
        for i in tender.get("cancellations", [])
        if i["status"] == "unsuccessful" and getattr(i, "complaints", None) and i["relatedLot"] == lot_id
    ])

    if (
        request.authenticated_role == "tender_owner"
        and (
            any([
                i for i in tender["cancellations"]
                if i["elatedLot"] and i["status"] == "pending" and i["relatedLot"] == lot_id])
            or not accept_lot
        )
    ):
        raise_operation_error(
            request,
            "Can't update qualification with pending cancellation lot",
        )


def validate_qualification_document_operation_not_in_allowed_status(request, **_):
    if request.validated["tender"]["status"] != "active.pre-qualification":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({request.validated['tender']['status']}) tender status"
        )


def validate_qualification_document_operation_not_in_pending(request, **_):
    qualification = request.validated["qualification"]
    if qualification["status"] != "pending":
        raise_operation_error(
            request, f"Can't {OPERATIONS.get(request.method)} document in current qualification status"
        )


# CONTRACT
def validate_contract_operation_not_in_allowed_status(request, **_):
    status = request.validated["tender"]["status"]
    if status not in ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} contract in current ({status}) tender status"
        )


def validate_update_contract_value_net_required(request, name="value", **_):
    data = request.validated["data"]
    value = data.get("value")

    if value is not None and "status" in request.validated["json_data"]:
        contract_amount_net = value.get("amountNet")
        if contract_amount_net is None:
            raise_operation_error(request, {"amountNet": BaseType.MESSAGES["required"]}, status=422, name=name)


def validate_update_contract_value_with_award(request, **_):
    data = request.validated["data"]
    updated_value = data.get("value")

    if updated_value and {"status", "value"} & set(request.validated["json_data"].keys()):
        award = [award for award in request.validated["tender"].get("awards", [])
                 if award.get("id") == request.validated["contract"].get("awardID")][0]

        _contracts_values = get_contracts_values_related_to_patched_contract(
            request.validated["tender"].get("contracts"),
            request.validated["contract"]["id"], updated_value,
            request.validated["contract"].get("awardID")
        )

        amount = sum([to_decimal(value.get("amount", 0)) for value in _contracts_values])
        amount_net = sum([to_decimal(value.get("amountNet", 0)) for value in _contracts_values])
        tax_included = updated_value.get("valueAddedTaxIncluded")
        if tax_included:
            if award.get("value", {}).get("valueAddedTaxIncluded"):
                if amount > to_decimal(award.get("value", {}).get("amount")):
                    raise_operation_error(request, "Amount should be less or equal to awarded amount", name="value")
            else:
                if amount_net > to_decimal(award.get("value", {}).get("amount")):
                    raise_operation_error(request, "AmountNet should be less or equal to awarded amount", name="value")
        else:
            if amount > to_decimal(award.get("value", {}).get("amount")):
                raise_operation_error(request, "Amount should be less or equal to awarded amount", name="value")


def validate_update_contract_value_amount(request, name="value", allow_equal=False, **_):
    data = request.validated["data"]
    contract_value = data.get(name)
    value = data.get("value") or data.get(name)
    if contract_value and {"status", name} & set(request.validated["json_data"].keys()):
        amount = to_decimal(contract_value.get("amount") or 0)
        amount_net = to_decimal(contract_value.get("amountNet") or 0)
        tax_included = value.get("valueAddedTaxIncluded")

        if not (amount == 0 and amount_net == 0):
            if tax_included:
                amount_max = (amount_net * AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_UP)
                if (amount <= amount_net or amount > amount_max) and not allow_equal:
                    raise_operation_error(
                        request,
                        "Amount should be greater than amountNet and differ by "
                        "no more than {}%".format(AMOUNT_NET_COEF * 100 - 100),
                        name=name,
                    )
                elif (amount < amount_net or amount > amount_max) and allow_equal:
                    raise_operation_error(
                        request,
                        f"Amount should be equal or greater than amountNet and differ by "
                        f"no more than {AMOUNT_NET_COEF * 100 - 100}%",
                        name=name,
                    )
            else:
                if amount != amount_net:
                    raise_operation_error(request, "Amount and amountNet should be equal", name=name)


def validate_update_contract_status_by_supplier(request, **_):
    if request.authenticated_role == "contract_supplier":
        data = request.validated["data"]
        if (
                "status" in data
                and data["status"] != "pending"
                or request.validated["contract"]["status"] != "pending.winner-signing"
        ):
            raise_operation_error(request, "Supplier can change status to `pending`")


def validate_update_contract_status_base(request, allowed_statuses_from, allowed_statuses_to, **_):
    tender = request.validated["tender"]

    # Contract statuses before and after current change
    current_status = request.validated["contract"]["status"]
    new_status = request.validated["data"].get("status", current_status)

    # Allow change contract status to cancelled for multi buyers tenders
    multi_contracts = len(tender.get("buyers", [])) > 1
    if multi_contracts:
        allowed_statuses_to = allowed_statuses_to + ("cancelled",)

    # Validate status change
    if (
        current_status != new_status
        and (
            current_status not in allowed_statuses_from
            or new_status not in allowed_statuses_to
        )
    ):
        raise_operation_error(request, "Can't update contract status")

    not_cancelled_contracts_count = sum(
        1 for contract in tender.get("contracts", [])
        if (
            contract.get("status") != "cancelled"
            and contract.get("awardID") == request.validated["contract"]["awardID"]
        )
    )
    if multi_contracts and new_status == "cancelled" and not_cancelled_contracts_count == 1:
        raise_operation_error(
            request,
            f"Can't update contract status from {current_status} to {new_status} "
            f"for last not cancelled contract. Cancel award instead."
        )


def validate_update_contract_status(request, **_):
    allowed_statuses_from = ("pending", "pending.winner-signing",)
    allowed_statuses_to = ("active", "pending", "pending.winner-signing",)
    validate_update_contract_status_base(
        request,
        allowed_statuses_from,
        allowed_statuses_to
    )


def validate_update_contract_only_for_active_lots(request, **_):
    tender = request.validated["tender"]
    contract = request.validated["contract"]

    award_lot_ids = []
    for award in tender.get("awards", []):
        if award.get("id") == contract.get("awardID"):
            award_lot_ids.append(award.get("lotID"))

    for lot in tender.get("lots", []):
        if lot.get("status") != "active" and lot.get("id") in award_lot_ids:
            raise_operation_error(request, "Can update contract only in active lot status")


def validate_update_contract_value(request, **_):
    data = request.validated["data"]
    value = data.get("value")
    if value:
        field = request.validated["contract"].get("value")
        if field and value.get("currency") != field.get("currency"):
            raise_operation_error(request, "Can't update currency for contract value", name="value")


def validate_contract_input_data(model, supplier_model):
    def validated(request, **_):
        if request.authenticated_role == "contract_supplier":
            validate = validate_input_data(supplier_model)
        else:
            validate = validate_input_data(model)
        return validate(request, **_)
    return validated


# CONTRACT DOCUMENT
def validate_role_for_contract_document_operation(request, **_):
    if request.authenticated_role not in ("tender_owner", "contract_supplier"):
        raise_operation_error(
            request,
            f"Can {OPERATIONS.get(request.method)} document only buyer or supplier"
        )
    if (
            request.authenticated_role == "contract_supplier" and
            request.validated["contract"]["status"] != "pending.winner-signing"
    ):
        raise_operation_error(
            request,
            f"Supplier can't {OPERATIONS.get(request.method)} document in current contract status"
        )
    if (
            request.authenticated_role == "tender_owner" and
            request.validated["contract"]["status"] == "pending.winner-signing"
    ):
        raise_operation_error(
            request,
            f"Tender owner can't {OPERATIONS.get(request.method)} document in current contract status"
        )


def validate_contract_document_status(operation):
    def validate(request, **_):
        tender_status = request.validated["tender"]["status"]
        if tender_status not in ("active.qualification", "active.awarded"):
            raise_operation_error(
                request,
                f"Can't {operation} document in current ({tender_status}) tender status"
            )
        elif request.validated["tender"].get("lots"):
            contract_lots = set()
            for award in request.validated["tender"].get("awards", []):
                if award["id"] == request.validated["contract"]["awardID"]:
                    contract_lots.add(award["lotID"])
            for lot in request.validated["tender"]["lots"]:
                if lot.get("id") in contract_lots and lot["status"] != "active":
                    raise_operation_error(request, f"Can {operation} document only in active lot status")
        if request.validated["contract"]["status"] not in ("pending", "pending.winner-signing", "active"):
            raise_operation_error(request, f"Can't {operation} document in current contract status")
    return validate

# lot


validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot",
    ("active.tendering", "draft", "draft.stage2")
)


def validate_tender_period_extension(request: Request, **_) -> None:
    extra_period = request.content_configurator.tendering_period_extra
    tender = request.validated["tender"]
    end_date = parse_date(tender["tenderPeriod"]["endDate"])
    if calculate_tender_business_date(get_now(), extra_period, tender) > end_date:
        raise_operation_error(request, "tenderPeriod should be extended by {0.days} days".format(extra_period))


def validate_operation_with_lot_cancellation_in_pending(type_name: str) -> callable:
    def validation(request: Request, **_) -> None:
        fields_names = {
            "lot": "id",
            "award": "lotID",
            "qualification": "lotID",
            "complaint": "relatedLot",
            "question": "relatedItem"
        }

        tender = request.validated["tender"]
        tender_created = get_first_revision_date(tender, default=get_now())

        field = fields_names.get(type_name)
        o = request.validated.get(type_name)
        lot_id = getattr(o, field, None)

        if tender_created < RELEASE_2020_04_19 or not lot_id:
            return

        msg = "Can't {} {} with lot that have active cancellation"
        if type_name == "lot":
            msg = "Can't {} lot that have active cancellation"

        accept_lot = all([
            any([j["status"] == "resolved" for j in i["complaints"]])
            for i in tender.get("cancellations", [])
            if i["status"] == "unsuccessful" and getattr(i, "complaints", None) and i["relatedLot"] == lot_id
        ])

        if (
            request.authenticated_role == "tender_owner"
            and (
                any([
                    i for i in tender.get("cancellations", [])
                    if i["relatedLot"] and i["status"] == "pending" and i["relatedLot"] == lot_id])
                or not accept_lot
            )
        ):
            raise_operation_error(
                request,
                msg.format(OPERATIONS.get(request.method), type_name),
            )
    return validation


def _validate_related_criterion(request: Request, relatedItem_id: str, action="cancel", relatedItem="lot") -> None:
    tender = request.validated["tender"]
    tender_creation_date = get_first_revision_date(tender, default=get_now())
    if tender_creation_date < CRITERION_REQUIREMENT_STATUSES_FROM:
        return
    if tender.get("criteria"):
        related_criteria = [
            criterion
            for criterion in tender["criteria"]
            for rg in criterion.get("requirementGroups", "")
            for requirement in rg.get("requirements", "")
            if criterion.get("relatedItem", "") == relatedItem_id and requirement["status"] == "active"
        ]
        if related_criteria:
            raise_operation_error(
                request, "Can't {} {} {} while related criterion has active requirements".format(
                    action, relatedItem_id, relatedItem
                )
            )


def _validate_related_object(request: Request, collection_name: str, lot_id: str) -> None:
    tender = request.validated["tender"]
    exist_related_obj = any(i.get("relatedLot", "") == lot_id for i in tender.get(collection_name, ""))

    if exist_related_obj:
        raise_operation_error(request, f"Cannot delete lot with related {collection_name}", status=422)


def validate_delete_lot_related_object(request: Request, **_) -> None:
    # We have some realization of that's validations in tender
    # This logic is duplicated
    lot_id = request.validated["lot"]["id"]
    _validate_related_criterion(request, lot_id, action="delete")
    _validate_related_object(request, "cancellations", lot_id)
    _validate_related_object(request, "milestones", lot_id)
    _validate_related_object(request, "items", lot_id)


# Criteria
def base_validate_operation_ecriteria_objects(request, valid_statuses="", obj_name="tender"):
    _validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
    current_status = request.validated[obj_name]["status"]
    if current_status not in valid_statuses:
        raise_operation_error(request, "Can't {} object if {} not in {} statuses".format(
            request.method.lower(), obj_name, valid_statuses))
