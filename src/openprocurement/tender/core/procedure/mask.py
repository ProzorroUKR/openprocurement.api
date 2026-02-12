from openprocurement.api.mask import (
    MASK_NUMBER,
    MASK_STRING,
    MASK_STRING_EN,
    compile_mask_mapping,
    optimize_tender_mask_mapping,
)

TENDER_MASK_MAPPING_RAW = {
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
    # documents
    # Note: title should be masked last, so we can still use it to identify the document
    # documents - notice
    "$.documents[?(@.documentType=='notice')].url": MASK_STRING,
    "$.documents[?(@.documentType=='notice')].title": MASK_STRING,
    # documents - sign.p7s
    "$.documents[?(@.title=='sign.p7s')].url": MASK_STRING,
    "$.documents[?(@.title=='sign.p7s')].title": MASK_STRING,
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
    "$.bids[*].tenderers[*].contactPoint.email": MASK_STRING,
    "$.bids[*].tenderers[*].contactPoint.faxNumber": MASK_STRING,
    "$.bids[*].tenderers[*].contactPoint.url": MASK_STRING,
    "$.bids[*].tenderers[*].contactPoint.name": MASK_STRING,
    "$.bids[*].tenderers[*].contactPoint.name_en": MASK_STRING_EN,
    "$.bids[*].tenderers[*].contactPoint.name_ru": MASK_STRING,
    # bids.tenderers.additionalContactPoints
    "$.bids[*].tenderers[*].additionalContactPoints[*].telephone": MASK_STRING,
    "$.bids[*].tenderers[*].additionalContactPoints[*].email": MASK_STRING,
    "$.bids[*].tenderers[*].additionalContactPoints[*].faxNumber": MASK_STRING,
    "$.bids[*].tenderers[*].additionalContactPoints[*].url": MASK_STRING,
    "$.bids[*].tenderers[*].additionalContactPoints[*].name": MASK_STRING,
    "$.bids[*].tenderers[*].additionalContactPoints[*].name_en": MASK_STRING_EN,
    "$.bids[*].tenderers[*].additionalContactPoints[*].name_ru": MASK_STRING,
    # bids.tenderers.scale
    "$.bids[*].tenderers[*].scale": MASK_STRING,
    # bids.participationUrl
    "$.bids[*].participationUrl": MASK_STRING,
    "$.bids[*].lotValues[*].participationUrl": MASK_STRING,
    # bids.subcontractingDetails
    "$.bids[*].subcontractingDetails": MASK_STRING,
    "$.bids[*].lotValues[*].subcontractingDetails": MASK_STRING,
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
    "$.awards[*].suppliers[*].contactPoint.email": MASK_STRING,
    "$.awards[*].suppliers[*].contactPoint.faxNumber": MASK_STRING,
    "$.awards[*].suppliers[*].contactPoint.url": MASK_STRING,
    "$.awards[*].suppliers[*].contactPoint.name": MASK_STRING,
    "$.awards[*].suppliers[*].contactPoint.name_en": MASK_STRING_EN,
    "$.awards[*].suppliers[*].contactPoint.name_ru": MASK_STRING,
    # awards.suppliers.additionalContactPoints
    "$.awards[*].suppliers[*].additionalContactPoints[*].telephone": MASK_STRING,
    "$.awards[*].suppliers[*].additionalContactPoints[*].email": MASK_STRING,
    "$.awards[*].suppliers[*].additionalContactPoints[*].faxNumber": MASK_STRING,
    "$.awards[*].suppliers[*].additionalContactPoints[*].url": MASK_STRING,
    "$.awards[*].suppliers[*].additionalContactPoints[*].name": MASK_STRING,
    "$.awards[*].suppliers[*].additionalContactPoints[*].name_en": MASK_STRING_EN,
    "$.awards[*].suppliers[*].additionalContactPoints[*].name_ru": MASK_STRING,
    # bids.tenderers.scale
    "$.awards[*].suppliers[*].scale": MASK_STRING,
    # contracts.items.deliveryDate
    "$.contracts[*].items[*].deliveryDate.startDate": MASK_STRING,
    "$.contracts[*].items[*].deliveryDate.endDate": MASK_STRING,
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
    # contracts.suppliers.scale
    "$.contracts[*].suppliers[*].scale": MASK_STRING,
    # bids.documents
    "$.bids[*].documents[*].title": MASK_STRING,
    "$.bids[*].documents[*].url": MASK_STRING,
    "$.bids[*].documents[*].confidentialityRationale": MASK_STRING,
    # bids.eligibilityDocuments
    "$.bids[*].eligibilityDocuments[*].title": MASK_STRING,
    "$.bids[*].eligibilityDocuments[*].url": MASK_STRING,
    "$.bids[*].eligibilityDocuments[*].confidentialityRationale": MASK_STRING,
    # bids.qualificationDocuments
    "$.bids[*].qualificationDocuments[*].title": MASK_STRING,
    "$.bids[*].qualificationDocuments[*].url": MASK_STRING,
    "$.bids[*].qualificationDocuments[*].confidentialityRationale": MASK_STRING,
    # bids.financialDocuments
    "$.bids[*].financialDocuments[*].title": MASK_STRING,
    "$.bids[*].financialDocuments[*].url": MASK_STRING,
    "$.bids[*].financialDocuments[*].confidentialityRationale": MASK_STRING,
    # awards.documents
    "$.awards[*].documents[*].title": MASK_STRING,
    "$.awards[*].documents[*].url": MASK_STRING,
    # contracts.documents
    "$.contracts[*].documents[*].title": MASK_STRING,
    "$.contracts[*].documents[*].url": MASK_STRING,
    # questions
    "$.questions[*].title": MASK_STRING,
    "$.questions[*].description": MASK_STRING,
    "$.questions[*].answer": MASK_STRING,
    # questions.author
    "$.questions[*].author.name": MASK_STRING,
    "$.questions[*].author.name_en": MASK_STRING_EN,
    "$.questions[*].author.name_ru": MASK_STRING,
    # questions.author.identifier
    "$.questions[*].author.identifier.id": MASK_STRING,
    "$.questions[*].author.identifier.legalName": MASK_STRING,
    "$.questions[*].author.identifier.legalName_en": MASK_STRING_EN,
    "$.questions[*].author.identifier.legalName_ru": MASK_STRING,
    # questions.author.address
    "$.questions[*].author.address.streetAddress": MASK_STRING,
    "$.questions[*].author.address.locality": MASK_STRING,
    "$.questions[*].author.address.region": MASK_STRING,
    "$.questions[*].author.address.postalCode": MASK_STRING,
    "$.questions[*].author.address.countryName": MASK_STRING,
    "$.questions[*].author.address.countryName_en": MASK_STRING_EN,
    "$.questions[*].author.address.countryName_ru": MASK_STRING,
    # complaints.author.contactPoint
    "$.questions[*].author.contactPoint.telephone": MASK_STRING,
    "$.questions[*].author.contactPoint.email": MASK_STRING,
    "$.questions[*].author.contactPoint.faxNumber": MASK_STRING,
    "$.questions[*].author.contactPoint.url": MASK_STRING,
    "$.questions[*].author.contactPoint.name": MASK_STRING,
    "$.questions[*].author.contactPoint.name_en": MASK_STRING_EN,
    "$.questions[*].author.contactPoint.name_ru": MASK_STRING,
    # complaints.author.additionalContactPoints
    "$.questions[*].author.additionalContactPoints[*].telephone": MASK_STRING,
    "$.questions[*].author.additionalContactPoints[*].email": MASK_STRING,
    "$.questions[*].author.additionalContactPoints[*].faxNumber": MASK_STRING,
    "$.questions[*].author.additionalContactPoints[*].url": MASK_STRING,
    "$.questions[*].author.additionalContactPoints[*].name": MASK_STRING,
    "$.questions[*].author.additionalContactPoints[*].name_en": MASK_STRING_EN,
    "$.questions[*].author.additionalContactPoints[*].name_ru": MASK_STRING,
    # complaints.documents
    "$..complaints[*].documents[*].title": MASK_STRING,
    "$..complaints[*].documents[*].url": MASK_STRING,
    # complaints.posts.documents
    "$..complaints[*].posts[*].documents[*].title": MASK_STRING,
    "$..complaints[*].posts[*].documents[*].url": MASK_STRING,
    # complaints
    "$..complaints[*].title": MASK_STRING,
    "$..complaints[*].description": MASK_STRING,
    "$..complaints[*].objections[*].title": MASK_STRING,
    "$..complaints[*].objections[*].description": MASK_STRING,
    "$..complaints[*].objections[*].classification.description": MASK_STRING,
    "$..complaints[*].objections[*].requestedRemedies[*].type": MASK_STRING,
    "$..complaints[*].objections[*].requestedRemedies[*].description": MASK_STRING,
    "$..complaints[*].objections[*].arguments[*].description": MASK_STRING,
    "$..complaints[*].objections[*].arguments[*].evidences[*].title": MASK_STRING,
    "$..complaints[*].objections[*].arguments[*].evidences[*].description": MASK_STRING,
    "$..complaints[*].resolution": MASK_STRING,
    "$..complaints[*].tendererAction": MASK_STRING,
    "$..complaints[*].decision": MASK_STRING,
    "$..complaints[*].rejectReasonDescription": MASK_STRING,
    "$..complaints[*].reviewPlace": MASK_STRING,
    "$..complaints[*].cancellationReason": MASK_STRING,
    "$..complaints[*].posts[*].title": MASK_STRING,
    "$..complaints[*].posts[*].description": MASK_STRING,
    # complaints.author
    "$..complaints[*].author.name": MASK_STRING,
    "$..complaints[*].author.name_en": MASK_STRING_EN,
    "$..complaints[*].author.name_ru": MASK_STRING,
    # complaints.author.identifier
    "$..complaints[*].author.identifier.id": MASK_STRING,
    "$..complaints[*].author.identifier.legalName": MASK_STRING,
    "$..complaints[*].author.identifier.legalName_en": MASK_STRING_EN,
    "$..complaints[*].author.identifier.legalName_ru": MASK_STRING,
    # complaints.author.address
    "$..complaints[*].author.address.streetAddress": MASK_STRING,
    "$..complaints[*].author.address.locality": MASK_STRING,
    "$..complaints[*].author.address.region": MASK_STRING,
    "$..complaints[*].author.address.postalCode": MASK_STRING,
    "$..complaints[*].author.address.countryName": MASK_STRING,
    "$..complaints[*].author.address.countryName_en": MASK_STRING_EN,
    "$..complaints[*].author.address.countryName_ru": MASK_STRING,
    # complaints.author.contactPoint
    "$..complaints[*].author.contactPoint.telephone": MASK_STRING,
    "$..complaints[*].author.contactPoint.email": MASK_STRING,
    "$..complaints[*].author.contactPoint.faxNumber": MASK_STRING,
    "$..complaints[*].author.contactPoint.url": MASK_STRING,
    "$..complaints[*].author.contactPoint.name": MASK_STRING,
    "$..complaints[*].author.contactPoint.name_en": MASK_STRING_EN,
    "$..complaints[*].author.contactPoint.name_ru": MASK_STRING,
    # complaints.author.additionalContactPoints
    "$..complaints[*].author.additionalContactPoints[*].telephone": MASK_STRING,
    "$..complaints[*].author.additionalContactPoints[*].email": MASK_STRING,
    "$..complaints[*].author.additionalContactPoints[*].faxNumber": MASK_STRING,
    "$..complaints[*].author.additionalContactPoints[*].url": MASK_STRING,
    "$..complaints[*].author.additionalContactPoints[*].name": MASK_STRING,
    "$..complaints[*].author.additionalContactPoints[*].name_en": MASK_STRING_EN,
    "$..complaints[*].author.additionalContactPoints[*].name_ru": MASK_STRING,
}

TENDER_MASK_MAPPING_REPLACEMENT_RULES = {
    "$..complaints": [
        "$.complaints",
        "$.awards[*].complaints",
        "$.qualifications[*].complaints",
        "$.cancellations[*].complaints",
    ],
}

TENDER_MASK_MAPPING_OPTIMIZED = optimize_tender_mask_mapping(
    TENDER_MASK_MAPPING_RAW,
    TENDER_MASK_MAPPING_REPLACEMENT_RULES,
)

TENDER_MASK_MAPPING = compile_mask_mapping(TENDER_MASK_MAPPING_OPTIMIZED)
