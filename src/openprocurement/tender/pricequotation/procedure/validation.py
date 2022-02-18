from openprocurement.api.validation import OPERATIONS, raise_operation_error
from openprocurement.tender.core.procedure.validation import validate_item_owner
from schematics.exceptions import ValidationError


def validate_bid_value(tender, value):
    if not value:
        raise ValidationError("This field is required.")
    if tender["value"]["amount"] < value["amount"]:
        raise ValidationError("value of bid should be less than value of tender")
    if tender["value"].get("currency") != value.get("currency"):
        raise ValidationError("currency of bid should be identical to currency of value of tender")
    if tender["value"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical " "to valueAddedTaxIncluded of value of tender"
        )


# awards
def validate_pq_award_owner(request, **kwargs):
    tender = request.validated["tender"]
    award = request.validated["award"]
    has_prev_awards = any(
        a['status'] != 'pending'
        for a in tender.get("awards", [])
        if a["bid_id"] == award["bid_id"] and a["id"] != award["id"]
    )
    if has_prev_awards or award["status"] != 'pending':
        owner_validation = validate_item_owner("tender")
    else:
        owner_validation = validate_item_owner("bid")
    return owner_validation(request, **kwargs)


# tender documents
def validate_document_operation_in_not_allowed_period(request, **_):
    status = request.validated["tender"]["status"]
    if status not in ("active.tendering", "draft"):
        operation = OPERATIONS.get(request.method)
        raise_operation_error(
            request,
            f"Can't {operation} document in current ({status}) tender status"
        )


def unless_administrator_or_bots(*validations):
    def decorated(request, **_):
        if request.authenticated_role  not in ("bots", "Administrator"):
            for validation in validations:
                validation(request)
    return decorated
