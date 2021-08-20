from openprocurement.api.utils import get_now, raise_operation_error, handle_data_exceptions
from openprocurement.api.validation import (
    validate_json_data,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
)
from openprocurement.tender.core.validation import TYPEMAP
from openprocurement.tender.core.procedure.utils import is_item_owner, apply_data_patch, delete_nones
from openprocurement.tender.core.procedure.documents import check_document_batch, check_document, update_document_url
from schematics.exceptions import ValidationError
from decimal import Decimal


def validate_input_data(input_model, allow_bulk=False, filters=None):
    """
    :param input_model: a model to validate data against
    :param allow_bulk: if True, request.validated["data"] will be a list of valid inputs
    :param filters: list of filter function that applied on valid data
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
            # if None is passed it should be added to the result
            # None means that the field value is deleted
            # IMPORTANT: input_data can contain more fields than are allowed to update
            # validate_data will raise Rogue field error then
            result = {k: v
                      for k, v in input_data.items()
                      if v is None
                      or isinstance(v, list) and len(v) == 0}
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


def validate_data(request, model, data):
    with handle_data_exceptions(request):
        instance = model(data)
        instance.validate()
        data = instance.serialize()
    return data


def validate_data_documents(request, **kwargs):
    data = request.validated["data"]
    for key in data.keys():
        if key == "documents" or "Documents" in key:
            if data[key]:
                docs = []
                for document in data[key]:
                    # some magic, yep
                    route_kwargs = {"bid_id": data["id"]}
                    document = check_document_batch(request, document, key, route_kwargs)
                    docs.append(document)

                # replacing documents in request.validated["data"]
                if docs:
                    data[key] = docs
    return data


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


def validate_bid_accreditation_level(request, **kwargs):
    # TODO: find a way to define accreditation without Model, like config of view attributes
    # TODO: Model should only validate passed data structure and types
    _validate_accreditation_level(request, request.tender_model.edit_accreditations, "bid", "creation")

    mode = request.validated["tender"].get("mode", None)
    _validate_accreditation_level_mode(request, mode, "bid", "creation")


def validate_bid_operation_period(request, **kwargs):
    tender = request.validated["tender"]
    tender_periond = tender.get("tenderPeriod", {})
    if (
        tender_periond.get("startDate")
        and get_now().isoformat() < tender_periond.get("startDate")
        or get_now().isoformat() > tender_periond.get("endDate", "")  # TODO: may "endDate" be missed ?
    ):
        operation = "added" if request.method == "POST" else "deleted"
        if request.authenticated_role != "Administrator" and request.method in ("PUT", "PATCH"):
            operation = "updated"
        raise_operation_error(
            request,
            "Bid can be {} only during the tendering period: from ({}) to ({}).".format(
                operation,
                tender_periond.get("startDate"),
                tender_periond.get("endDate"),
            ),
        )


def validate_bid_operation_not_in_tendering(request, **kwargs):
    status = request.validated["tender"]["status"]
    if status != "active.tendering":
        operation = "add" if request.method == "POST" else "delete"
        if request.authenticated_role != "Administrator" and request.method in ("PUT", "PATCH"):
            operation = "update"
        raise_operation_error(
            request, "Can't {} bid in current ({}) tender status".format(operation, status)
        )


def validate_lotvalue_value(tender, related_lot, value):
    if value or related_lot:
        for lot in tender.get("lots", ""):
            if lot and lot["id"] == related_lot:
                tender_lot_value = lot.get("value")
                if float(tender_lot_value["amount"]) < value.amount:
                    raise ValidationError("value of bid should be less than value of lot")
                if tender_lot_value["currency"] != value.currency:
                    raise ValidationError("currency of bid should be identical to currency of value of lot")
                if tender_lot_value["valueAddedTaxIncluded"] != value.valueAddedTaxIncluded:
                    raise ValidationError(
                        "valueAddedTaxIncluded of bid should be identical " "to valueAddedTaxIncluded of value of lot"
                    )


def validate_bid_value(tender, value):
    if tender.get("lots"):
        if value:
            raise ValidationError("value should be posted for each lot of bid")
    else:
        tender_value = tender.get("value")
        if not value:
            raise ValidationError("This field is required.")
        if Decimal(tender_value["amount"]) < value.amount:
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


def validate_relatedlot(tender, relatedLot):
    if relatedLot not in [lot["id"] for lot in tender.get("lots") if lot]:
        raise ValidationError("relatedLot should be one of lots")


def validate_view_bid_document(request, **kwargs):
    tender_status = request.validated["tender"]["status"]
    if tender_status in ("active.tendering", "active.auction") \
       and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_view_bids(request, **kwargs):
    tender_status = request.validated["tender"]["status"]
    if tender_status in ("active.tendering", "active.auction"):
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", tender_status
            ),
        )


def validate_update_deleted_bid(request, **kwargs):
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
    force_replace = ("id", "datePublished", "author")
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
