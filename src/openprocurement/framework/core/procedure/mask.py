from openprocurement.api.mask import (
    MASK_STRING,
    MASK_STRING_EN,
    compile_mask_mapping,
)

SUBMISSION_MASK_MAPPING = compile_mask_mapping(
    {
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
        "$.tenderers[*].contactPoint.email": MASK_STRING,
        "$.tenderers[*].contactPoint.faxNumber": MASK_STRING,
        "$.tenderers[*].contactPoint.url": MASK_STRING,
        "$.tenderers[*].contactPoint.name": MASK_STRING,
        "$.tenderers[*].contactPoint.name_en": MASK_STRING_EN,
        "$.tenderers[*].contactPoint.name_ru": MASK_STRING,
        # documents
        "$..documents[*].title": MASK_STRING,
        "$..documents[*].url": MASK_STRING,
    }
)

QUALIFICATION_MASK_MAPPING = compile_mask_mapping(
    {
        # documents
        "$..documents[*].title": MASK_STRING,
        "$..documents[*].url": MASK_STRING,
    }
)

AGREEMENT_MASK_MAPPING = compile_mask_mapping(
    {
        # contracts.suppliers.address
        "$.contracts[*].suppliers[*].address.streetAddress": MASK_STRING,
        "$.contracts[*].suppliers[*].address.locality": MASK_STRING,
        "$.contracts[*].suppliers[*].address.region": MASK_STRING,
        "$.contracts[*].suppliers[*].address.postalCode": MASK_STRING,
        "$.contracts[*].suppliers[*].address.countryName": MASK_STRING,
        "$.contracts[*].suppliers[*].address.countryName_en": MASK_STRING_EN,
        "$.contracts[*].suppliers[*].address.countryName_ru": MASK_STRING,
        # contracts.suppliers.contactPoint
        "$.contracts[*].suppliers[*].contactPoint.telephone": MASK_STRING,
        "$.contracts[*].suppliers[*].contactPoint.email": MASK_STRING,
        "$.contracts[*].suppliers[*].contactPoint.faxNumber": MASK_STRING,
        "$.contracts[*].suppliers[*].contactPoint.url": MASK_STRING,
        "$.contracts[*].suppliers[*].contactPoint.name": MASK_STRING,
        "$.contracts[*].suppliers[*].contactPoint.name_en": MASK_STRING_EN,
        "$.contracts[*].suppliers[*].contactPoint.name_ru": MASK_STRING,
        # contracts.suppliers.additionalContactPoints
        "$.contracts[*].suppliers[*].additionalContactPoints[*].telephone": MASK_STRING,
        "$.contracts[*].suppliers[*].additionalContactPoints[*].email": MASK_STRING,
        "$.contracts[*].suppliers[*].additionalContactPoints[*].faxNumber": MASK_STRING,
        "$.contracts[*].suppliers[*].additionalContactPoints[*].url": MASK_STRING,
        "$.contracts[*].suppliers[*].additionalContactPoints[*].name": MASK_STRING,
        "$.contracts[*].suppliers[*].additionalContactPoints[*].name_en": MASK_STRING_EN,
        "$.contracts[*].suppliers[*].additionalContactPoints[*].name_ru": MASK_STRING,
        # documents
        "$..documents[*].title": MASK_STRING,
        "$..documents[*].url": MASK_STRING,
    }
)
