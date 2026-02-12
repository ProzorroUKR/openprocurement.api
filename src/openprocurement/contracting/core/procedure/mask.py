from openprocurement.api.mask import (
    MASK_NUMBER,
    MASK_STRING,
    MASK_STRING_EN,
    compile_mask_mapping,
    optimize_tender_mask_mapping,
)

CONTRACT_MASK_MAPPING_RAW = {
    # items.deliveryDate
    "$.items[*].deliveryDate.startDate": MASK_STRING,
    "$.items[*].deliveryDate.endDate": MASK_STRING,
    # items.deliveryAddress
    "$.items[*].deliveryAddress.streetAddress": MASK_STRING,
    "$.items[*].deliveryAddress.locality": MASK_STRING,
    "$.items[*].deliveryAddress.region": MASK_STRING,
    "$.items[*].deliveryAddress.postalCode": MASK_STRING,
    "$.items[*].deliveryAddress.countryName": MASK_STRING,
    "$.items[*].deliveryAddress.countryName_en": MASK_STRING_EN,
    "$.items[*].deliveryAddress.countryName_ru": MASK_STRING,
    # items.deliveryLocation
    "$.items[*].deliveryLocation.latitude": MASK_NUMBER,
    "$.items[*].deliveryLocation.longitude": MASK_NUMBER,
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
    "$.suppliers[*].contactPoint.email": MASK_STRING,
    "$.suppliers[*].contactPoint.faxNumber": MASK_STRING,
    "$.suppliers[*].contactPoint.url": MASK_STRING,
    "$.suppliers[*].contactPoint.name": MASK_STRING,
    "$.suppliers[*].contactPoint.name_en": MASK_STRING_EN,
    "$.suppliers[*].contactPoint.name_ru": MASK_STRING,
    # suppliers.additionalContactPoints
    "$.suppliers[*].additionalContactPoints[*].telephone": MASK_STRING,
    "$.suppliers[*].additionalContactPoints[*].email": MASK_STRING,
    "$.suppliers[*].additionalContactPoints[*].faxNumber": MASK_STRING,
    "$.suppliers[*].additionalContactPoints[*].url": MASK_STRING,
    "$.suppliers[*].additionalContactPoints[*].name": MASK_STRING,
    "$.suppliers[*].additionalContactPoints[*].name_en": MASK_STRING_EN,
    "$.suppliers[*].additionalContactPoints[*].name_ru": MASK_STRING,
    # suppliers.scale
    "$.suppliers[*].scale": MASK_STRING,
    # suppliers.signerInfo
    "$.suppliers[*].signerInfo.name": MASK_STRING,
    "$.suppliers[*].signerInfo.email": MASK_STRING,
    "$.suppliers[*].signerInfo.telephone": MASK_STRING,
    "$.suppliers[*].signerInfo.iban": MASK_STRING,
    "$.suppliers[*].signerInfo.position": MASK_STRING,
    "$.suppliers[*].signerInfo.authorizedBy": MASK_STRING,
    # changes
    "$.changes[*].rationale": MASK_STRING,
    "$.changes[*].rationale_ru": MASK_STRING,
    "$.changes[*].rationale_en": MASK_STRING,
    # documents
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,
}

CONTRACT_MASK_MAPPING_REPLACEMENT_RULES = {
    "$..documents": [
        "$.documents",
        "$.implementation.transactions[*].documents",
    ],
}

CONTRACT_MASK_MAPPING_OPTIMIZED = optimize_tender_mask_mapping(
    CONTRACT_MASK_MAPPING_RAW,
    CONTRACT_MASK_MAPPING_REPLACEMENT_RULES,
)

CONTRACT_MASK_MAPPING = compile_mask_mapping(CONTRACT_MASK_MAPPING_OPTIMIZED)
