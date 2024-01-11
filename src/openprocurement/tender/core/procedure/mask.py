from openprocurement.api.mask import (
    MASK_STRING,
    MASK_STRING_EN,
    MASK_NUMBER,
    MASK_DATE,
)

TENDER_MASK_MAPPING = {

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

    # quantity
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

    # value
    "$.value.amount": MASK_NUMBER,
    "$.lots[*].value.amount": MASK_NUMBER,

    # minimalStep
    "$.minimalStep.amount": MASK_NUMBER,
    "$.lots[*].minimalStep.amount": MASK_NUMBER,

    # guarantee
    "$.guarantee.amount": MASK_NUMBER,
    "$.lots[*].guarantee.amount": MASK_NUMBER,

    # criteria
    "$.criteria[*].title": MASK_STRING,
    "$.criteria[*].requirementGroups[*].description": MASK_STRING,
    "$.criteria[*].requirementGroups[*].requirements[*].title": MASK_STRING,
    "$.criteria[*].requirementGroups[*].requirements[*].description": MASK_STRING,

    # bids.tenderers
    "$.bids[*].tenderers[*].name": MASK_STRING,
    "$.bids[*].tenderers[*].name_en": MASK_STRING_EN,
    "$.bids[*].tenderers[*].name_ru": MASK_STRING,

    # bids.tenderers.identifier
    "$.bids[*].tenderers[*].identifier.id": MASK_STRING,
    "$.bids[*].tenderers[*].identifier.legalName": MASK_STRING,
    "$.bids[*].tenderers[*].identifier.legalName_en": MASK_STRING_EN,
    "$.bids[*].tenderers[*].identifier.legalName_ru": MASK_STRING,

    # bids.tenderers.address
    "$.bids[*].tenderers[*].address.streetAddress": MASK_STRING,
    "$.bids[*].tenderers[*].address.locality": MASK_STRING,
    "$.bids[*].tenderers[*].address.region": MASK_STRING,
    "$.bids[*].tenderers[*].address.postalCode": MASK_STRING,
    "$.bids[*].tenderers[*].address.countryName": MASK_STRING,
    "$.bids[*].tenderers[*].address.countryName_en": MASK_STRING_EN,
    "$.bids[*].tenderers[*].address.countryName_ru": MASK_STRING,

    # bids.tenderers.contactPoint
    "$.bids[*].tenderers[*].contactPoint.telephone": MASK_STRING,
    "$.bids[*].tenderers[*].contactPoint.url": MASK_STRING,
    "$.bids[*].tenderers[*].contactPoint.name": MASK_STRING,

    # bids.value
    "$.bids[*].value.amount": MASK_NUMBER,
    "$.bids[*].lotValues[*].value.amount": MASK_NUMBER,

    # bids.weightedValue
    "$.bids[*].weightedValue.amount": MASK_NUMBER,
    "$.bids[*].lotValues[*].weightedValue.amount": MASK_NUMBER,

    # bids.requirementResponses
    "$.bids[*].requirementResponses[*].title": MASK_STRING,
    "$.bids[*].requirementResponses[*].description": MASK_STRING,
    "$.bids[*].requirementResponses[*].requirement.title": MASK_STRING,
    "$.bids[*].requirementResponses[*].evidences[*].title": MASK_STRING,
    "$.bids[*].requirementResponses[*].evidences[*].relatedDocument.title": MASK_STRING,

    # auctionUrl
    "$.auctionUrl": MASK_STRING,
    "$.lots[*].auctionUrl": MASK_STRING,

    # auctionPeriod
    "$.auctionPeriod.shouldStartAfter": MASK_DATE,
    "$.auctionPeriod.startDate": MASK_DATE,
    "$.auctionPeriod.endDate": MASK_DATE,
    "$.lots[*].auctionPeriod.shouldStartAfter": MASK_DATE,
    "$.lots[*].auctionPeriod.startDate": MASK_DATE,
    "$.lots[*].auctionPeriod.endDate": MASK_DATE,

    # awards.value
    "$.awards[*].value.amount": MASK_NUMBER,

    # awards.weightedValue
    "$.awards[*].weightedValue.amount": MASK_NUMBER,

    # awards.suppliers
    "$.awards[*].suppliers[*].name": MASK_STRING,
    "$.awards[*].suppliers[*].name_en": MASK_STRING_EN,
    "$.awards[*].suppliers[*].name_ru": MASK_STRING,

    # awards.suppliers.identifier
    "$.awards[*].suppliers[*].identifier.id": MASK_STRING,
    "$.awards[*].suppliers[*].identifier.legalName": MASK_STRING,
    "$.awards[*].suppliers[*].identifier.legalName_en": MASK_STRING_EN,
    "$.awards[*].suppliers[*].identifier.legalName_ru": MASK_STRING,

    # awards.suppliers.address
    "$.awards[*].suppliers[*].address.streetAddress": MASK_STRING,
    "$.awards[*].suppliers[*].address.locality": MASK_STRING,
    "$.awards[*].suppliers[*].address.region": MASK_STRING,
    "$.awards[*].suppliers[*].address.postalCode": MASK_STRING,
    "$.awards[*].suppliers[*].address.countryName": MASK_STRING,
    "$.awards[*].suppliers[*].address.countryName_en": MASK_STRING_EN,
    "$.awards[*].suppliers[*].address.countryName_ru": MASK_STRING,

    # awards.suppliers.contactPoint
    "$.awards[*].suppliers[*].contactPoint.telephone": MASK_STRING,
    "$.awards[*].suppliers[*].contactPoint.url": MASK_STRING,
    "$.awards[*].suppliers[*].contactPoint.name": MASK_STRING,

    # contracts.items.quantity
    "$.contracts[*].items[*].quantity": MASK_NUMBER,

    # contracts.items.deliveryDate
    "$.contracts[*].items[*].deliveryDate.startDate": MASK_DATE,
    "$.contracts[*].items[*].deliveryDate.endDate": MASK_DATE,

    # contracts.items.deliveryAddress
    "$.contracts[*].items[*].deliveryAddress.streetAddress": MASK_STRING,
    "$.contracts[*].items[*].deliveryAddress.locality": MASK_STRING,
    "$.contracts[*].items[*].deliveryAddress.region": MASK_STRING,
    "$.contracts[*].items[*].deliveryAddress.postalCode": MASK_STRING,
    "$.contracts[*].items[*].deliveryAddress.countryName": MASK_STRING,
    "$.contracts[*].items[*].deliveryAddress.countryName_en": MASK_STRING_EN,
    "$.contracts[*].items[*].deliveryAddress.countryName_ru": MASK_STRING,

    # contracts.items.deliveryLocation
    "$.contracts[*].items[*].deliveryLocation.latitude": MASK_NUMBER,
    "$.contracts[*].items[*].deliveryLocation.longitude": MASK_NUMBER,

    # contracts.suppliers
    "$.contracts[*].suppliers[*].name": MASK_STRING,
    "$.contracts[*].suppliers[*].name_en": MASK_STRING_EN,
    "$.contracts[*].suppliers[*].name_ru": MASK_STRING,

    # contracts.suppliers.identifier
    "$.contracts[*].suppliers[*].identifier.id": MASK_STRING,
    "$.contracts[*].suppliers[*].identifier.legalName": MASK_STRING,
    "$.contracts[*].suppliers[*].identifier.legalName_en": MASK_STRING_EN,
    "$.contracts[*].suppliers[*].identifier.legalName_ru": MASK_STRING,

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
    "$.contracts[*].suppliers[*].contactPoint.url": MASK_STRING,
    "$.contracts[*].suppliers[*].contactPoint.name": MASK_STRING,

    # contracts.value
    "$.contracts[*].value.amount": MASK_NUMBER,
    "$.contracts[*].value.amountNet": MASK_NUMBER,

    # documents
    #   recursive search for all documents like:
    #   bids.documents, qualifications.documents, awards.documents, etc
    "$..documents[*].documentType": MASK_STRING,
    "$..documents[*].title": MASK_STRING,
    "$..documents[*].url": MASK_STRING,

}
