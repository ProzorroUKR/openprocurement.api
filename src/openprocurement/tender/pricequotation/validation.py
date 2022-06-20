from schematics.types import DateTimeType
from schematics.exceptions import ValidationError
from openprocurement.api.utils import raise_operation_error, get_first_revision_date
from openprocurement.api.constants import PQ_CRITERIA_RESPONSES_ALL_FROM
from openprocurement.api.validation import validate_data, OPERATIONS, validate_json_data
from openprocurement.api.models import (
    StrictStringType,
    StrictIntType,
    StrictDecimalType,
    StrictBooleanType,
)
from openprocurement.tender.pricequotation.constants import PROFILE_PATTERN
from openprocurement.tender.core.validation import validate_value_factory


TYPEMAP = {
    'string': StrictStringType(),
    'integer': StrictIntType(),
    'number': StrictDecimalType(),
    'boolean': StrictBooleanType(),
    'date-time': DateTimeType(),
}

# Criteria


validate_value_type = validate_value_factory(TYPEMAP)


def validate_list_of_values_type(values, datatype):
    if not values:
        return
    if not isinstance(values, (list, tuple, set)):
        raise ValidationError("Values should be list")
    for value in values:
        validate_value_type(value, datatype)


# tender documents
def validate_document_operation_in_not_allowed_period(request, **kwargs):
    if request.validated["tender_status"] not in ["active.tendering", "draft"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# award
def validate_create_award_not_in_allowed_period(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status != "active.qualification":
        raise_operation_error(
            request,
            "Can't create award in current ({}) tender status".format(
                tender.status
            )
        )


def validate_award_update_in_terminal_status(request, **kwargs):
    award_status = request.validated['award'].status
    if award_status in ('cancelled', 'unsuccessful'):
        raise_operation_error(
            request,
            "Can't update award in current ({}) status".format(
                award_status
            )
        )


# contract document
def validate_contract_document_operation(request, **kwargs):
    operation = OPERATIONS.get(request.method)
    if request.validated["tender_status"] not in\
       ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                operation, request.validated["tender_status"]
            ),
        )
    if request.validated["contract"].status not in ["pending", "active"]:
        raise_operation_error(
            request,
            "Can't {} document in current contract status".format(operation)
        )
    return True


def validate_patch_tender_data(request, **kwargs):
    model = type(request.tender)
    data = validate_data(request, model, True, validate_json_data(request))
    _validate_kind_update(request, model)
    return data


def _validate_kind_update(request, model):
    data = request.validated["data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    if kind and kind not in model.procuring_entity_kinds:
        request.errors.add(
            "body", "kind",
            "{kind!r} procuringEntity cannot publish this type of procedure. Only {kinds} are allowed.".format(
                kind=kind, kinds=", ".join(model.procuring_entity_kinds)
            )
        )
        request.errors.status = 403


def _validate_bid_value(tender, value):
    if not value:
        raise ValidationError("This field is required.")
    if tender.value.amount < value.amount:
        raise ValidationError("value of bid should be less than value of tender")
    if tender.get("value").currency != value.currency:
        raise ValidationError("currency of bid should be identical to currency of value of tender")
    if tender.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical " "to valueAddedTaxIncluded of value of tender"
        )


def validate_post_bid(request, **kwargs):
    bid = request.validated["bid"]
    tender = request.validated["tender"]
    tenderer_id = bid["tenderers"][0]["identifier"]["id"]
    if tenderer_id not in [i.identifier.id for i in tender.shortlistedFirms]:
        raise_operation_error(request, f"Can't add bid if tenderer not in shortlistedFirms")


def validate_tender_publish(request, **kwargs):
    current_status = request.validated['tender'].status
    tender_status = request.validated['data'].get('status', current_status)
    error_message = "{} can't switch tender from status ({}) to ({})"
    if tender_status == current_status:
        return
    if current_status == "draft.publishing" and tender_status == "cancelled":
        raise_operation_error(request,
                              error_message.format("You",
                                                   current_status,
                                                   tender_status))
    if request.authenticated_role not in ("bots", "Administrator", "chronograph") \
            and tender_status != "draft.publishing":
        raise_operation_error(request,
                              error_message.format(request.authenticated_role,
                                                   current_status,
                                                   tender_status))


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
            raise ValidationError(
                "expectedMinItems couldn't be higher then count of items in expectedValues"
            )

        if expected_max_items and expected_max_items > len(expected_values):
            raise ValidationError(
                "expectedMaxItems couldn't be higher then count of items in expectedValues"
            )

    elif expected_min_items or expected_max_items:
        raise ValidationError(
            "expectedMinItems and expectedMaxItems couldn't exist without expectedValues"
        )


def validate_requirement_values(requirement):

    field_conflict_map = {
        "expectedValue": ["minValue", "maxValue", "expectedValues"],
        "expectedValues": ["minValue", "maxValue", "expectedValue"],
    }

    for k, v in field_conflict_map.items():
        if (
                requirement.get(k) is not None
                and any(requirement.get(i) is not None for i in v)
        ):
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
