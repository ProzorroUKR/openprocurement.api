from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import (
    validate_data,
    validate_json_data,
    OPERATIONS
    )


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
