from openprocurement.api.mask import (
    MASK_STRING,
    MASK_STRING_EN,
    MASK_NUMBER,
    MASK_DATE,
)

SUBMISSION_MASK_MAPPING = {

    # tenderers.address
    "$.tenderers[*].address.streetAddress": MASK_STRING,
    "$.tenderers[*].address.locality": MASK_STRING,
    "$.tenderers[*].address.region": MASK_STRING,
    "$.tenderers[*].address.postalCode": MASK_STRING,
    "$.tenderers[*].address.countryName": MASK_STRING,
    "$.tenderers[*].address.countryName_en": MASK_STRING_EN,
    "$.tenderers[*].address.countryName_ru": MASK_STRING,

    # tenderers.contactPoint
    "$.tenderers[*].contactPoint.telephone": MASK_STRING,
    "$.tenderers[*].contactPoint.url": MASK_STRING,
    "$.tenderers[*].contactPoint.name": MASK_STRING,

    # documents
    "$..documents[*].documentType": MASK_STRING,
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,

}

QUALIFICATION_MASK_MAPPING = {

    # documents
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,

}

AGREEMENT_MASK_MAPPING = {

    # suppliers.address
    "$.contracts[*].suppliers[*].address.streetAddress": MASK_STRING,
    "$.contracts[*].suppliers[*].address.locality": MASK_STRING,
    "$.contracts[*].suppliers[*].address.region": MASK_STRING,
    "$.contracts[*].suppliers[*].address.postalCode": MASK_STRING,
    "$.contracts[*].suppliers[*].address.countryName": MASK_STRING,
    "$.contracts[*].suppliers[*].address.countryName_en": MASK_STRING_EN,
    "$.contracts[*].suppliers[*].address.countryName_ru": MASK_STRING,

    # suppliers.contactPoint
    "$.contracts[*].suppliers[*].contactPoint.telephone": MASK_STRING,
    "$.contracts[*].suppliers[*].contactPoint.url": MASK_STRING,
    "$.contracts[*].suppliers[*].contactPoint.name": MASK_STRING,

    # documents
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,

}
