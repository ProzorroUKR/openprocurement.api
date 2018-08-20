from openprocurement.agreement.cfaua.models.change import Change
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import (
    validate_data,
    validate_json_data,
    OPERATIONS
    )

from openprocurement.api.utils import update_logging_context, error_handler, raise_operation_error

def validate_agreement_patch(request):
    data = validate_json_data(request)
    model = request.agreement_from_data(data, create=False)
    return validate_data(request, model, True, data=data)


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
    return validate_data(request, Change, data=data)


def validate_agreement_change_add_not_in_allowed_agreement_status(request):
    agreement = request.validated['agreement']
    if agreement.status != 'active':
        raise_operation_error(request, 'Can\'t add agreement change in current ({}) agreement status'.format(agreement.status))


def validate_create_agreement_change(request):
    agreement = request.validated['agreement']
    if agreement.changes and agreement.changes[-1].status == 'pending':
        raise_operation_error(request, 'Can\'t create new agreement change while any (pending) change exists')


def validate_patch_change_data(request):
    return validate_data(request, Change, True)


def validate_agreement_change_update_not_in_allowed_change_status(request):
    change = request.validated['change']
    if change.status == 'active':
        raise_operation_error(request, 'Can\'t update agreement change in current ({}) status'.format(change.status))


def validate_update_agreement_change_status(request):
    data = request.validated['data']
    if not data.get("dateSigned", ''):
        raise_operation_error(request, 'Can\'t update agreement change status. \'dateSigned\' is required.')
