from openprocurement.api.mask import (
    MASK_STRING,
    MASK_STRING_EN,
    MASK_NUMBER,
    MASK_DATE,
)

SUBMISSION_MASK_MAPPING = {

    # tenderers
    "$.tenderers[*].name": MASK_STRING,
    "$.tenderers[*].name_en": MASK_STRING_EN,
    "$.tenderers[*].name_ru": MASK_STRING,

    # tenderers.identifier
    "$.tenderers[*].identifier.id": MASK_STRING,
    "$.tenderers[*].identifier.legalName": MASK_STRING,
    "$.tenderers[*].identifier.legalName_en": MASK_STRING_EN,
    "$.tenderers[*].identifier.legalName_ru": MASK_STRING,

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
    "$..documents[*].documentType": MASK_STRING,
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,
}

AGREEMENT_MASK_MAPPING = {

    # procuringEntity
    "$.procuringEntity.name": MASK_STRING,
    "$.procuringEntity.name_en": MASK_STRING_EN,
    "$.procuringEntity.name_ru": MASK_STRING,

    # procuringEntity.identifier
    "$.procuringEntity.identifier.id": MASK_STRING,
    "$.procuringEntity.identifier.legalName": MASK_STRING,
    "$.procuringEntity.identifier.legalName_en": MASK_STRING_EN,
    "$.procuringEntity.identifier.legalName_ru": MASK_STRING,

    # procuringEntity.address
    "$.procuringEntity.address.streetAddress": MASK_STRING,
    "$.procuringEntity.address.locality": MASK_STRING,
    "$.procuringEntity.address.region": MASK_STRING,
    "$.procuringEntity.address.postalCode": MASK_STRING,
    "$.procuringEntity.address.countryName": MASK_STRING,
    "$.procuringEntity.address.countryName_en": MASK_STRING_EN,
    "$.procuringEntity.address.countryName_ru": MASK_STRING,

    # procuringEntity.contactPoint
    "$.procuringEntity.contactPoint.telephone": MASK_STRING,
    "$.procuringEntity.contactPoint.url": MASK_STRING,
    "$.procuringEntity.contactPoint.name": MASK_STRING,

    # suppliers
    "$.suppliers[*].name": MASK_STRING,
    "$.suppliers[*].name_en": MASK_STRING_EN,
    "$.suppliers[*].name_ru": MASK_STRING,

    # suppliers.identifier
    "$.suppliers[*].identifier.id": MASK_STRING,
    "$.suppliers[*].identifier.legalName": MASK_STRING,
    "$.suppliers[*].identifier.legalName_en": MASK_STRING_EN,
    "$.suppliers[*].identifier.legalName_ru": MASK_STRING,

    # suppliers.address
    "$.suppliers[*].address.streetAddress": MASK_STRING,
    "$.suppliers[*].address.locality": MASK_STRING,
    "$.suppliers[*].address.region": MASK_STRING,
    "$.suppliers[*].address.postalCode": MASK_STRING,
    "$.suppliers[*].address.countryName": MASK_STRING,
    "$.suppliers[*].address.countryName_en": MASK_STRING_EN,
    "$.suppliers[*].address.countryName_ru": MASK_STRING,

    # suppliers.contactPoint
    "$.suppliers[*].contactPoint.telephone": MASK_STRING,
    "$.suppliers[*].contactPoint.url": MASK_STRING,
    "$.suppliers[*].contactPoint.name": MASK_STRING,

    # documents
    "$..documents[*].documentType": MASK_STRING,
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,
}
