from schematics.exceptions import ValidationError
from schematics.types import DateTimeType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.types import (
    StrictBooleanType,
    StrictDecimalType,
    StrictIntType,
    StrictStringType,
)
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.validation import validate_value_factory
from openprocurement.tender.pricequotation.constants import PROFILE_PATTERN


def validate_bid_value(tender, value):
    if not value:
        raise ValidationError("This field is required.")
    config = get_tender()["config"]
    if config.get("valueCurrencyEquality"):
        if tender["value"].get("currency") != value.get("currency"):
            raise ValidationError("currency of bid should be identical to currency of value of tender")
        if config.get("hasValueRestriction") and tender["value"]["amount"] < value["amount"]:
            raise ValidationError("value of bid should be less than value of tender")
    if tender["value"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
        )


# tender documents
def validate_document_operation_in_not_allowed_period(request, **_):
    status = request.validated["tender"]["status"]
    if status not in ("active.tendering", "draft"):
        operation = OPERATIONS.get(request.method)
        raise_operation_error(request, f"Can't {operation} document in current ({status}) tender status")


def validate_contract_document_status(operation):
    def validate(request, **_):
        tender_status = request.validated["tender"]["status"]
        if tender_status not in ["active.qualification", "active.awarded"]:
            raise_operation_error(request, f"Can't {operation} document in current ({tender_status}) tender status")
        if request.validated["contract"]["status"] not in ["pending", "active"]:
            raise_operation_error(request, f"Can't {operation} document in current contract status")

    return validate


# criteria
def validate_tender_criteria_existence(request, **_):
    tender = request.validated["tender"]
    data = request.validated["data"]
    new_tender_status = data.get("status", "draft")
    tender_criteria = tender["criteria"] if tender.get("criteria") else data.get("criteria")
    if new_tender_status != "draft" and not tender_criteria:
        raise_operation_error(request, f"Can't update tender to next ({new_tender_status}) status without criteria")


TYPEMAP = {
    'string': StrictStringType(),
    'integer': StrictIntType(),
    'number': StrictDecimalType(),
    'boolean': StrictBooleanType(),
    'date-time': DateTimeType(),
}
validate_value_type = validate_value_factory(TYPEMAP)


def validate_list_of_values_type(values, datatype):
    if not values:
        return
    if not isinstance(values, (list, tuple, set)):
        raise ValidationError("Values should be list")
    for value in values:
        validate_value_type(value, datatype)


def validate_profile_pattern(profile):
    result = PROFILE_PATTERN.findall(profile)
    if len(result) != 1:
        raise ValidationError("The profile value doesn't match id pattern")


def validate_expected_items(requirement):
    expected_min_items = requirement.get("expectedMinItems")
    expected_max_items = requirement.get("expectedMaxItems")
    expected_values = requirement.get("expectedValues")

    if expected_values:
        if expected_min_items and expected_max_items and expected_min_items > expected_max_items:
            raise ValidationError("expectedMinItems couldn't be higher then expectedMaxItems")

        if expected_min_items and expected_min_items > len(expected_values):
            raise ValidationError("expectedMinItems couldn't be higher then count of items in expectedValues")

        if expected_max_items and expected_max_items > len(expected_values):
            raise ValidationError("expectedMaxItems couldn't be higher then count of items in expectedValues")

    elif expected_min_items or expected_max_items:
        raise ValidationError("expectedMinItems and expectedMaxItems couldn't exist without expectedValues")


def validate_requirement_values(requirement):
    field_conflict_map = {
        "expectedValue": ["minValue", "maxValue", "expectedValues"],
        "expectedValues": ["minValue", "maxValue", "expectedValue"],
    }

    for k, v in field_conflict_map.items():
        if requirement.get(k) is not None and any(requirement.get(i) is not None for i in v):
            raise ValidationError(f"{k} conflicts with {v}")
    validate_expected_items(requirement)


def validate_requirement(requirement):
    required_fields = ('expectedValue', 'expectedValues', 'minValue', 'maxValue')
    if all(requirement.get(i) is None for i in required_fields):
        raise ValidationError(
            'Value required for at least one field ["expectedValues", "expectedValue", "minValue", "maxValue"]'
        )
    validate_requirement_values(requirement)


def validate_requirement_groups(value):
    for requirement_group in value:
        for requirement in requirement_group.requirements or "":
            validate_requirement(requirement)
