from jsonpath_ng import parse


MASK_STRING = "Приховано"
MASK_STRING_EN = "Hidden"
MASK_NUMBER = 0.0
MASK_INTEGER = 0
MASK_DATE = '1111-11-11T00:00:00+02:00'

EXCLUDED_ROLES = (
    "brokers",
    "chronograph",
    "auction",
    "bots",
    "contracting",
    "competitive_dialogue",
    "agreements",
    "agreement_selection",
    "Administrator",
)

def mask_data(data, mask_mapping):
    for json_path, replacement_value in mask_mapping.items():
        jsonpath_expr = parse(json_path)
        jsonpath_expr.update(data, replacement_value)


def mask_object_data(request, data, mask_mapping):
    if not mask_mapping:
        # Nothing to mask
        return

    if not data.get("config", {}).get("restricted", False):
        # Masking only enabled if restricted is True
        return

    if request.authenticated_role in EXCLUDED_ROLES:
        # Masking is not required for these roles
        return

    mask_data(data, mask_mapping)
