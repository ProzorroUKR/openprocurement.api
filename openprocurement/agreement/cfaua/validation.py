from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import (
    validate_data,
    validate_json_data
    )


def validate_agreement_patch(request):
    data = validate_json_data(request)
    model = request.agreement_from_data(data, create=False)
    return validate_data(request, model, True, data=data)


def validate_credentials_generate(request):
    agreement = request.validated['agreement']
    if agreement.status != "active":
        raise_operation_error(
            request, "Can't generate credentials in current ({}) agreement status".format(agreement.status)
        )