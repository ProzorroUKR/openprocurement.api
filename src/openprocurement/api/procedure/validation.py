from openprocurement.tender.core.procedure.validation import validate_input_data, validate_patch_data


def validate_input_data_from_resolved_model():
    def validated(request, **_):
        state = request.root.state
        method = request.method.lower()
        model = getattr(state, f"get_{method}_data_model")()
        request.validated[f"{method}_data_model"] = model
        validate = validate_input_data(model)
        return validate(request, **_)
    return validated


def validate_patch_data_from_resolved_model(item_name):
    def validated(request, **_):
        state = request.root.state
        model = state.get_parent_patch_data_model()
        validate = validate_patch_data(model, item_name)
        return validate(request, **_)
    return validated
