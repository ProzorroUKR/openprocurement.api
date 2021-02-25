from decimal import Decimal

from schematics.exceptions import ValidationError

from openprocurement.api.utils import apply_data_patch, error_handler, raise_operation_error, update_logging_context
from openprocurement.api.utils import get_change_class
from openprocurement.api.validation import validate_data, validate_json_data, OPERATIONS


def validate_agreement_patch(request, **kwargs):
    data = validate_json_data(request)
    if data:
        if "features" in data:
            if apply_data_patch([f.serialize() for f in request.context.features], data["features"]):
                request.errors.add("body", "features", "Can't change features")
                request.errors.status = 403
                raise error_handler(request)

    return validate_data(request, type(request.agreement), True, data=data)


def validate_update_agreement_status(request, **kwargs):
    if request.context.changes:
        data = request.validated["data"]
        pending_changes = [c for c in request.context.changes if c["status"] == "pending"]
        if "status" in data and data["status"] == "terminated" and pending_changes:
            raise_operation_error(request, "Can't update agreement status with pending change.")


def validate_credentials_generate(request, **kwargs):
    agreement = request.validated["agreement"]
    if agreement.status != "active":
        raise_operation_error(
            request, "Can't generate credentials in current ({}) agreement status".format(agreement.status)
        )


def validate_document_operation_on_agreement_status(request, **kwargs):
    status = request.validated["agreement"].status
    if status != "active":
        raise_operation_error(
            request, "Can't {} document in current ({}) agreement status".format(OPERATIONS.get(request.method), status)
        )


def validate_change_data(request, **kwargs):
    update_logging_context(request, {"change_id": "__new__"})
    data = validate_json_data(request)
    _changes_models = request.agreement.__class__.changes.field
    if not "rationaleType" in data:
        raise_operation_error(request, "Can't add change without rationaleType")
    model = get_change_class(_changes_models, data, _validation=True)
    if not model:
        raise_operation_error(
            request,
            "rationaleType should be one of {}".format(
                ["taxRate", "itemPriceVariation", "thirdParty", "partyWithdrawal"]
            ),
        )
    return validate_data(request, model, data=data)


def validate_agreement_change_add_not_in_allowed_agreement_status(request, **kwargs):
    agreement = request.validated["agreement"]
    if agreement.status != "active":
        raise_operation_error(
            request, "Can't add agreement change in current ({}) agreement status".format(agreement.status)
        )


def validate_create_agreement_change(request, **kwargs):
    agreement = request.validated["agreement"]
    if agreement.changes and agreement.changes[-1].status == "pending":
        raise_operation_error(request, "Can't create new agreement change while any (pending) change exists")


def validate_patch_change_data(request, **kwargs):
    model = request.context.__class__
    return validate_data(request, model, True)


def validate_agreement_change_update_not_in_allowed_change_status(request, **kwargs):
    change = request.validated["change"]
    if change.status in {"active", "cancelled"}:
        raise_operation_error(request, "Can't update agreement change in current ({}) status".format(change.status))


def validate_update_agreement_change_status(request, **kwargs):
    data = request.validated["data"]
    if data["status"] == "active" and not data.get("dateSigned", ""):
        raise_operation_error(request, "Can't update agreement change status. 'dateSigned' is required.")


def validate_values_uniq(values):
    codes = [i.value for i in values]
    if any([codes.count(i) > 1 for i in set(codes)]):
        raise ValidationError("Feature value should be uniq for feature")


def validate_features_uniq(features):
    if features:
        codes = [i.code for i in features]
        if any([codes.count(i) > 1 for i in set(codes)]):
            raise ValidationError("Feature code should be uniq for all features")


def validate_parameters_uniq(parameters):
    if parameters:
        codes = [i.code for i in parameters]
        if [i for i in set(codes) if codes.count(i) > 1]:
            raise ValidationError("Parameter code should be uniq for all parameters")


# changes modifications validators


def validate_item_price_variation_modifications(modifications):
    for modification in modifications:
        if modification.addend:
            raise ValidationError("Only factor is allowed for itemPriceVariation type of change")
        if not Decimal("0.9") <= modification.factor <= Decimal("1.1"):
            raise ValidationError("Modification factor should be in range 0.9 - 1.1")


def validate_third_party_modifications(modifications):
    for modification in modifications:
        if modification.addend:
            raise ValidationError("Only factor is allowed for thirdParty type of change")


def validate_modifications_items_uniq(modifications):
    if modifications:
        agreement_items_id = {i.id for i in modifications[0].__parent__.__parent__.items or []}
        item_ids = {m.itemId for m in modifications if m.itemId in agreement_items_id}
        if len(item_ids) != len(modifications):
            raise ValidationError("Item id should be uniq for all modifications and one of agreement:items")


def validate_modifications_contracts_uniq(modifications):
    if modifications:
        agreement_contracts_id = {i.id for i in modifications[0].__parent__.__parent__.contracts}
        contracts_ids = {c.contractId for c in modifications if c.contractId in agreement_contracts_id}
        if len(contracts_ids) != len(modifications):
            raise ValidationError("Contract id should be uniq for all modifications and one of agreement:contracts")


def validate_only_addend_or_only_factor(modifications):
    if modifications:
        changes_with_addend_and_factor = [m for m in modifications if m.addend and m.factor]
        if changes_with_addend_and_factor:
            raise ValidationError("Change with taxRate rationaleType, can have only factor or only addend")
