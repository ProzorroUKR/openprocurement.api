# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context
from openprocurement.api.validation import (
    validate_json_data,
    validate_data,
    _validate_accreditation_level,
)


def validate_agreement_data(request, **kwargs):
    update_logging_context(request, {"agreement_id": "__new__"})
    data = validate_json_data(request)
    model = request.agreement_from_data(data, create=False)
    _validate_agreement_accreditation_level(request, model)
    return validate_data(request, model, data=data)


def _validate_agreement_accreditation_level(request, model):
    levels = model.create_accreditations
    _validate_accreditation_level(request, levels, "agreement", "creation")
