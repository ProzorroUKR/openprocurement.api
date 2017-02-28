# -*- coding: utf-8 -*-
from openprocurement.api.validation import validate_data
from openprocurement.api.utils import update_logging_context  # XXX tender context


def validate_complaint_data(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        return
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'complaint_id': '__new__'})
    model = type(request.context).complaints.model_class
    return validate_data(request, model)


def validate_patch_complaint_data(request):
    model = type(request.context.__parent__).complaints.model_class
    return validate_data(request, model, True)
