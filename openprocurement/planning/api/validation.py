# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.planning.api.models import Plan


def validate_plan_data(request):
    update_logging_context(request, {'plan_id': '__new__'})
    data = validate_json_data(request)
    if data is None:
        return
    model = request.plan_from_data(data, create=False)
    if hasattr(request, 'check_accreditation') \
            and not any([request.check_accreditation(acc) for acc in model.create_accreditations]):
        request.errors.add('plan', 'accreditation', 'Broker Accreditation level does not permit plan creation')
        request.errors.status = 403
        return
    data = validate_data(request, model, data=data)
    if data and data.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('plan', 'mode', 'Broker Accreditation level does not permit plan creation')
        request.errors.status = 403
        return
    return data


def validate_patch_plan_data(request):
    return validate_data(request, Plan, True)
