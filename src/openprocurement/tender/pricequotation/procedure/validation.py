from schematics.exceptions import ValidationError
from openprocurement.api.utils import raise_operation_error


def validate_post_bid_tenderers(request, **_):
    bid = request.validated["data"]
    tender = request.validated["tender"]
    tenderer_id = bid["tenderers"][0]["identifier"]["id"]
    if tenderer_id not in (i["identifier"]["id"] for i in tender.get("shortlistedFirms", "")):
        raise_operation_error(request, f"Can't add bid if tenderer not in shortlistedFirms")


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
