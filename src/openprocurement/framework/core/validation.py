from openprocurement.api.utils import update_logging_context, raise_operation_error
from openprocurement.api.validation import (
    validate_json_data,
    validate_accreditation_level,
    validate_data,
    validate_doc_accreditation_level_mode,
)


def validate_framework_accreditation_level_central(request, model):
    levels = model.central_accreditations
    validate_accreditation_level(request, levels, "frameworkType", "framework", "creation")


def validate_framework_data(request):
    update_logging_context(request, {"framework_id": "__new__"})
    data = validate_json_data(request)
    model = request.framework_from_data(data, create=False)
    validate_framework_accreditation_level_central(request, model)
    data = validate_data(request, model, data=data)
    validate_doc_accreditation_level_mode(request, "frameworkType", "framework")
    return data


def validate_patch_framework_data(request):
    data = validate_json_data(request)
    return validate_data(request, type(request.framework), True, data)


def validate_framework_patch_status(request, allowed_statuses=["draft"]):
    framework_status = request.validated["framework"].status
    if request.authenticated_role != "Administrator" and framework_status not in allowed_statuses:
        raise_operation_error(request, "Can't update tender in current ({}) status".format(framework_status))
