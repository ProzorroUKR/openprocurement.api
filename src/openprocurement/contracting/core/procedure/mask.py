from openprocurement.api.mask import (
    MASK_STRING,
    MASK_STRING_EN,
    MASK_NUMBER,
    MASK_DATE,
)

CONTRACT_MASK_MAPPING = {

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

    # items.quantity
    "$.items[*].quantity": MASK_NUMBER,

    # items.deliveryDate
    "$.items[*].deliveryDate.startDate": MASK_DATE,
    "$.items[*].deliveryDate.endDate": MASK_DATE,

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
    "$.suppliers[*].contactPoint.url": MASK_STRING,
    "$.suppliers[*].contactPoint.name": MASK_STRING,

    # value
    "$.value.amount": MASK_NUMBER,
    "$.value.amountNet": MASK_NUMBER,

    # documents
    "$..documents[*].documentType": MASK_STRING,
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,
}
