from jsonpath_ng.ext import parse

from openprocurement.api.auth import ACCR_RESTRICTED

MASK_STRING = "Приховано"
MASK_STRING_EN = "Hidden"
MASK_NUMBER = 0.0
MASK_INTEGER = 0
MASK_DATE = '1970-01-01T03:00:00+03:00'

EXCLUDED_ROLES = (
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
    for rule in mask_mapping.values():
        rule["expr"].update(data, rule["value"])


def compile_mask_mapping(mask_mapping):
    """
    Pre-compile the JSONPath expressions in the mask mapping for efficient reuse.
    """
    compiled_mapping = {}
    for path, value in mask_mapping.items():
        compiled_mapping[path] = {
            "value": value,
            "expr": parse(path),
        }
    return compiled_mapping


def mask_object_data(request, data, mask_mapping, mask_func=mask_data):
    if not mask_mapping:
        # Nothing to mask
        return

    config_restricted = data.get("config", {}).get("restricted", False)
    if config_restricted is not True:
        # Masking only enabled if restricted is True
        return

    if request.authenticated_role in EXCLUDED_ROLES:
        # Masking is not required for these roles
        return

    if request.authenticated_role == "brokers" and request.check_accreditations((ACCR_RESTRICTED,)):
        # Masking is not required for brokers with accreditation
        # that allows access to restricted data
        return

    from openprocurement.tender.core.procedure.utils import extract_document_id

    if extract_document_id(request) and request.params and request.params.get("download"):
        # Masking is not required when non-authorized user download document by link
        return

    # Extract revisions before masking
    revisions = data.pop("revisions", None)

    # Mask data
    mask_func(data, mask_mapping)

    # Restore revisions after masking
    data["revisions"] = revisions
