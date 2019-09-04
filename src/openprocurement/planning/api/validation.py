# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context, error_handler
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.planning.api.models import Plan


def validate_plan_data(request):
    update_logging_context(request, {'plan_id': '__new__'})
    data = validate_json_data(request)
    if data is None:
        return
    model = request.plan_from_data(data, create=False)
    if hasattr(request, 'check_accreditations') and not request.check_accreditations(model.create_accreditations):
        request.errors.add('plan', 'accreditation', 'Broker Accreditation level does not permit plan creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    data = validate_data(request, model, data=data)
    if data and data.get('mode', None) is None and request.check_accreditations(('t',)):
        request.errors.add('plan', 'mode', 'Broker Accreditation level does not permit plan creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    return data


def validate_patch_plan_data(request):
    return validate_data(request, Plan, True)


def validate_plan_has_not_tender(request):
    plan = request.validated['plan']
    if plan.tender_id:
        request.errors.add(
            "url", "id", u"This plan has already got a tender"
        )
        request.errors.status = 409
        raise error_handler(request.errors)


def validate_plan_with_tender(request):
    plan = request.validated['plan']
    if plan.tender_id and "procuringEntity" in request.validated['json_data']:
        request.errors.add(
            "data",
            "procuringEntity",
            "Changing this field is not allowed after tender creation"
        )
        request.errors.status = 422
        raise error_handler(request.errors)
