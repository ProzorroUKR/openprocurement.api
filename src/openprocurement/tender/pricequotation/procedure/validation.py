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
