from schematics.exceptions import ValidationError
from zope.component import queryAdapter

from openprocurement.api.utils import (
    apply_data_patch,
    error_handler,
    raise_operation_error,
    update_logging_context
)

from openprocurement.api.models import DecimalType
from openprocurement.api.validation import (
    validate_data,
    validate_json_data,
    OPERATIONS
    )
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.agreement.cfaua.interfaces import IChange


def validate_agreement_patch(request):
    data = validate_json_data(request)
    if data:
        if 'features' in data:
            if apply_data_patch([f.serialize() for f in request.context.features], data['features']):
                request.errors.add('body', 'features', 'Can\'t change features')
                request.errors.status = 403
                raise error_handler(request.errors)

    return validate_data(request, type(request.agreement), True, data=data)


def validate_credentials_generate(request):
    agreement = request.validated['agreement']
    if agreement.status != "active":
        raise_operation_error(
            request,
            "Can't generate credentials in current ({}) agreement status".format(agreement.status)
        )


def validate_document_operation_on_agreement_status(request):
    status = request.validated['agreement'].status
    if status != 'active':
        raise_operation_error(
            request,
            "Can't {} document in current ({}) agreement status".format(
                OPERATIONS.get(request.method),
                status
            )
        )


def validate_change_data(request):
    update_logging_context(request, {'change_id': '__new__'})
    data = validate_json_data(request)
    model = queryAdapter(IChange, IContentConfigurator, data['rationaleType'])
    return validate_data(request, model, data=data)


def validate_agreement_change_add_not_in_allowed_agreement_status(request):
    agreement = request.validated['agreement']
    if agreement.status != 'active':
        raise_operation_error(request, 'Can\'t add agreement change in current ({}) agreement status'.format(agreement.status))


def validate_create_agreement_change(request):
    agreement = request.validated['agreement']
    if agreement.changes and agreement.changes[-1].status == 'pending':
        raise_operation_error(request, 'Can\'t create new agreement change while any (pending) change exists')


def validate_patch_change_data(request):
    model = request.context.__class__
    return validate_data(request, model, True)


def validate_agreement_change_update_not_in_allowed_change_status(request):
    change = request.validated['change']
    if change.status == 'active':
        raise_operation_error(request, 'Can\'t update agreement change in current ({}) status'.format(change.status))


def validate_update_agreement_change_status(request):
    data = request.validated['data']
    if not data.get("dateSigned", ''):
        raise_operation_error(request, 'Can\'t update agreement change status. \'dateSigned\' is required.')


def validate_values_uniq(values, *args):
    codes = [i.value for i in values]
    if any([codes.count(i) > 1 for i in set(codes)]):
        raise ValidationError(u"Feature value should be uniq for feature")


def validate_features_uniq(features, *args):
    if features:
        codes = [i.code for i in features]
        if any([codes.count(i) > 1 for i in set(codes)]):
            raise ValidationError(u"Feature code should be uniq for all features")


def validate_parameters_uniq(parameters, *args):
    if parameters:
        codes = [i.code for i in parameters]
        if [i for i in set(codes) if codes.count(i) > 1]:
            raise ValidationError(u"Parameter code should be uniq for all parameters")


# changes modifications validators


def validate_item_price_variation_modifications(modifications, *args):
    for modification in modifications:
        if modification.addend:
            raise ValidationError(u"Only factor is allowed")
        if not DecimalType('0.9') <= modification.factor <= DecimalType('1.1'):
            raise ValidationError(u"Modification factor should be in range 0.9 - 1.1")


def validate_third_party_modifications(modifications, *args):
    for modification in modifications:
        if modification.addend:
            raise ValidationError(u"Only factor is allowed")


def validate_modifications_items_uniq(modifications, *args):
    if modifications:
        item_ids = {m.itemId for m in modifications}  # set of all items ids in modifications
        if len(item_ids) != len(modifications):
            raise ValidationError(u"Item id should be uniq for all modifications")
