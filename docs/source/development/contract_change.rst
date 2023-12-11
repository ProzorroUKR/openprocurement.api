.. _econtract_change_updated_flow:

EContract Change
================

This section describes the new workflow for making changes to active contracts.


Contract
--------

Imagine you already have active contract with all needed information:

.. sourcecode:: http

    GET /api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196 HTTP/1.0
    Authorization: Bearer broker
    Host: public-api-sandbox.prozorro.gov.ua


    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "awardID": "c220713cbd024586b6382ef97a852dc7",
        "contractID": "UA-2023-10-10-000001-a-1",
        "period": {
          "startDate": "2023-10-10T01:00:00+03:00",
          "endDate": "2024-10-09T01:00:00+03:00"
        },
        "dateSigned": "2023-10-10T01:00:00+03:00",
        "date": "2023-10-10T01:00:00+03:00",
        "dateModified": "2023-10-10T01:00:00+03:00",
        "dateCreated": "2023-10-10T01:00:00+03:00",
        "tender_id": "26fe592e6eb4454fb91865f39117fe4b",
        "owner": "broker",
        "documents": [
          {
            "id": "0042d18dfb254f4a8a0c166f1e980196",
            "hash": "md5:00000000000000000000000000000000",
            "title": "contract_first_document.doc",
            "format": "application/msword",
            "url": "http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents/0042d18dfb254f4a8a0c166f1e980196?download=d351f09369034d459a5cd87583381c73",
            "documentOf": "contract",
            "datePublished": "2023-10-10T01:00:00+03:00",
            "dateModified": "2023-10-10T01:00:00+03:00"
          },
          {
            "id": "9202cd64da8f42a5942c68dc14bf534a",
            "hash": "md5:00000000000000000000000000000000",
            "title": "contract_second_document.doc",
            "format": "application/msword",
            "url": "http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents/9202cd64da8f42a5942c68dc14bf534a?download=1ea9c5fa82c84b2a8206318bc86360df",
            "documentOf": "contract",
            "datePublished": "2023-10-10T01:00:00+03:00",
            "dateModified": "2023-10-10T01:00:00+03:00"
          }
        ],
        "status": "active",
        "buyer": {
          "name": "Державне управління справами",
          "identifier": {
            "scheme": "UA-EDR",
            "id": "00037256",
            "uri": "http://www.dus.gov.ua/"
          },
          "address": {
            "streetAddress": "вул. Банкова, 11, корпус 1",
            "locality": "м. Київ",
            "region": "м. Київ",
            "postalCode": "01220",
            "countryName": "Україна"
          },
          "signerInfo": {
            "name": "Test Testovich",
            "email": "example@email.com",
            "telephone": "+380950000000",
            "iban": "234234234234234",
            "position": "Генеральний директор",
            "authorizedBy": "Статут компанії"
          }
        },
        "suppliers": [
          {
            "name": "Державне управління справами",
            "identifier": {
              "scheme": "UA-EDR",
              "id": "00037256",
              "uri": "http://www.dus.gov.ua/"
            },
            "address": {
              "streetAddress": "вул. Банкова, 11, корпус 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "01220",
              "countryName": "Україна"
            },
            "signerInfo": {
              "name": "Test Testovich",
              "email": "example@email.com",
              "telephone": "+380950000000",
              "iban": "111111111111111",
              "position": "Генеральний директор",
              "authorizedBy": "Статут компанії"
            }
          }
        ],
        "items": [
          {
            "id": "d7ba05ad129d4380b139d363df055ec0",
            "description": "Комп’ютерне обладнання",
            "quantity": 5.0,
            "deliveryDate": {
              "startDate": "2023-10-12T01:00:00+03:00",
              "endDate": "2023-10-15T01:00:00+03:00"
            },
            "classification": {
              "description": "Комп’ютерне обладнанн",
              "scheme": "ДК021",
              "id": "30230000-0"
            },
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ],
            "deliveryAddress": {
              "streetAddress": "вул. Банкова 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "79000",
              "countryName": "Україна"
            },
            "unit": {
              "name": "штук",
              "value": {
                "amount": 12.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87"
            }
          },
          {
            "id": "98b99c56dacf48728e1a069205bdf6c2",
            "description": "Комп’ютерне обладнання",
            "quantity": 5.0,
            "deliveryDate": {
              "startDate": "2023-10-12T01:00:00+03:00",
              "endDate": "2023-10-15T01:00:00+03:00"
            },
            "classification": {
              "description": "Комп’ютерне обладнанн",
              "scheme": "ДК021",
              "id": "30230000-0"
            },
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ],
            "deliveryAddress": {
              "streetAddress": "вул. Банкова 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "79000",
              "countryName": "Україна"
            },
            "unit": {
              "name": "штук",
              "value": {
                "amount": 6.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87"
            }
          }
        ],
        "value": {
          "amount": 238.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true,
          "amountNet": 230.0
        },
        "bid_owner": "broker",
        "id": "eb4343b446004f47aa2ec7f6e542f196"
      }
    }


Creating change
---------------

Both buyer and supplier can make changes to the active contract.

When creating a change, you need to fill in three mandatory fields (in the old behavior there were only two: `rationale`, `rationaleTypes`):

:rationale:
    string, cause of changes

:rationaleTypes:
    list, types of change

:modifications:
    object, field that could be changed in contract

`modifications` is a new structure that represents fields that the user wants to update in the contract, these fields are of the same type as the corresponding fields in the contract:

:title:
    string, required

:description:
    string

:buyer:
    :ref:`EContractOrganization`

:suppliers:
    List of :ref:`EContractOrganization` objects

:items:
    List of :ref:`Item` objects

:value:
    :ref:`ContractValue` object

After explaining new structure, let's create change:

.. sourcecode:: http

    POST /api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/changes?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 267
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "rationale": "Опис причини змін контракту",
        "rationale_en": "Contract change cause",
        "rationaleTypes": [
          "volumeCuts",
          "priceReduction"
        ],
        "modifications": {
          "value": {
            "amount": 230.0,
            "currency": "UAH",
            "valueAddedTaxIncluded": true,
            "amountNet": 223.0
          }
        }
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json

    {
      "data": {
        "rationale": "Опис причини змін контракту",
        "rationale_en": "Contract change cause",
        "rationaleTypes": [
          "volumeCuts",
          "priceReduction"
        ],
        "modifications": {
          "value": {
            "amount": 230.0,
            "currency": "UAH",
            "valueAddedTaxIncluded": true,
            "amountNet": 223.0
          }
        }
        "id": "b9887678ba3c448b977467c0fe3ada31",
        "status": "pending",
        "date": "2023-10-10T01:00:00+03:00"
      }
    }


Activating change
------------------

In previous flow after creation contract change you need to set `dateSigned` to activate contract, in new flow for activating change supplier and buyer should add signature document with extension `.p7s` and documentType `contractChangeSignature` to change object.

Buyer add document to change:

.. sourcecode:: http

    POST /api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 333
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "documentType": "contractChangeSignature",
        "title": "buyer_sign.p7s",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=mFBbg4SYLP%2BQk4Cn6xwFtFp2XKpLLLIQmIqKvBsiciOF6nuiH7Gw9Wmk0IsPpNVvMLNn21PDO0c5XMfjxxX5Dw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents/32ec55c6c6144f7a8fceea1ed68a5290

    {
      "data": {
        "documentType": "contractChangeSignature",
        "hash": "md5:00000000000000000000000000000000",
        "title": "buyer_sign.p7s",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=cG1JU%2F1r%2B2jlQbXxJsq3HCYzzTi9mderkkqPwomMk34J6oAJ%2B7GRNC3kUgPO3zskbNjKkMkhiaJY2PmkUlOkBA%3D%3D&KeyID=a8968c46",
        "documentOf": "contract",
        "id": "32ec55c6c6144f7a8fceea1ed68a5290",
        "datePublished": "2023-10-10T01:00:00+03:00",
        "dateModified": "2023-10-10T01:00:00+03:00"
      }
    }

Supplier add document:

.. sourcecode:: http

    POST /api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 333
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "documentType": "contractChangeSignature",
        "title": "supplier_sign.p7s",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=mFBbg4SYLP%2BQk4Cn6xwFtFp2XKpLLLIQmIqKvBsiciOF6nuiH7Gw9Wmk0IsPpNVvMLNn21PDO0c5XMfjxxX5Dw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents/32ec55c6c6144f7a8fceea1ed68a5290

    {
      "data": {
        "documentType": "contractChangeSignature",
        "hash": "md5:00000000000000000000000000000000",
        "title": "supplier_sign.p7s",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=cG1JU%2F1r%2B2jlQbXxJsq3HCYzzTi9mderkkqPwomMk34J6oAJ%2B7GRNC3kUgPO3zskbNjKkMkhiaJY2PmkUlOkBA%3D%3D&KeyID=a8968c46",
        "documentOf": "contract",
        "id": "32ec55c6c6144f7a8fceea1ed68a5290",
        "datePublished": "2023-10-10T01:00:00+03:00",
        "dateModified": "2023-10-10T01:00:00+03:00"
      }
    }

After adding signature documents we have possibility to activate change:

.. sourcecode:: http

    PATCH /api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/changes/b9887678ba3c448b977467c0fe3ada31?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 73
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active",
        "dateSigned": "2023-10-10T01:00:00+03:00"
      }
    }


    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "rationale": "Друга і третя поставка має бути розфасована",
        "rationale_en": "Contract change cause",
        "rationaleTypes": [
          "volumeCuts",
          "priceReduction"
        ],
        "modifications": {
          "value": {
            "amount": 230.0,
            "currency": "UAH",
            "valueAddedTaxIncluded": true,
            "amountNet": 223.0
          }
        },
        "previousValues": {
          "value": {
            "amount": 238.0,
            "currency": "UAH",
            "valueAddedTaxIncluded": true,
            "amountNet": 230.0
          }
        }
        "dateSigned": "2023-10-10T01:00:00+03:00",
        "id": "b9887678ba3c448b977467c0fe3ada31",
        "status": "active",
        "date": "2023-10-10T01:00:00+03:00"
      }
    }

After activation, a new `previousValues` field appears, which contains information about the previous values of changed fields in the contract.

Also after activation, changes from the `modifications` field are applied to the contract:

.. sourcecode:: http

    GET /api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196 HTTP/1.0
    Authorization: Bearer broker
    Host: public-api-sandbox.prozorro.gov.ua


    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "awardID": "c220713cbd024586b6382ef97a852dc7",
        "contractID": "UA-2023-10-10-000001-a-1",
        "period": {
          "startDate": "2023-10-10T01:00:00+03:00",
          "endDate": "2024-10-09T01:00:00+03:00"
        },
        "dateSigned": "2023-10-10T01:00:00+03:00",
        "date": "2023-10-10T01:00:00+03:00",
        "dateModified": "2023-10-10T01:00:00+03:00",
        "dateCreated": "2023-10-10T01:00:00+03:00",
        "tender_id": "26fe592e6eb4454fb91865f39117fe4b",
        "owner": "broker",
        "documents": [
          {
            "id": "0042d18dfb254f4a8a0c166f1e980196",
            "hash": "md5:00000000000000000000000000000000",
            "title": "contract_first_document.doc",
            "format": "application/msword",
            "url": "http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents/0042d18dfb254f4a8a0c166f1e980196?download=d351f09369034d459a5cd87583381c73",
            "documentOf": "contract",
            "datePublished": "2023-10-10T01:00:00+03:00",
            "dateModified": "2023-10-10T01:00:00+03:00"
          },
          {
            "id": "9202cd64da8f42a5942c68dc14bf534a",
            "hash": "md5:00000000000000000000000000000000",
            "title": "contract_second_document.doc",
            "format": "application/msword",
            "url": "http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/eb4343b446004f47aa2ec7f6e542f196/documents/9202cd64da8f42a5942c68dc14bf534a?download=1ea9c5fa82c84b2a8206318bc86360df",
            "documentOf": "contract",
            "datePublished": "2023-10-10T01:00:00+03:00",
            "dateModified": "2023-10-10T01:00:00+03:00"
          }
        ],
        "status": "active",
        "buyer": {
          "name": "Державне управління справами",
          "identifier": {
            "scheme": "UA-EDR",
            "id": "00037256",
            "uri": "http://www.dus.gov.ua/"
          },
          "address": {
            "streetAddress": "вул. Банкова, 11, корпус 1",
            "locality": "м. Київ",
            "region": "м. Київ",
            "postalCode": "01220",
            "countryName": "Україна"
          },
          "signerInfo": {
            "name": "Test Testovich",
            "email": "example@email.com",
            "telephone": "+380950000000",
            "iban": "234234234234234",
            "position": "Генеральний директор",
            "authorizedBy": "Статут компанії"
          }
        },
        "suppliers": [
          {
            "name": "Державне управління справами",
            "identifier": {
              "scheme": "UA-EDR",
              "id": "00037256",
              "uri": "http://www.dus.gov.ua/"
            },
            "address": {
              "streetAddress": "вул. Банкова, 11, корпус 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "01220",
              "countryName": "Україна"
            },
            "signerInfo": {
              "name": "Test Testovich",
              "email": "example@email.com",
              "telephone": "+380950000000",
              "iban": "111111111111111",
              "position": "Генеральний директор",
              "authorizedBy": "Статут компанії"
            }
          }
        ],
        "items": [
          {
            "id": "d7ba05ad129d4380b139d363df055ec0",
            "description": "Комп’ютерне обладнання",
            "quantity": 5.0,
            "deliveryDate": {
              "startDate": "2023-10-12T01:00:00+03:00",
              "endDate": "2023-10-15T01:00:00+03:00"
            },
            "classification": {
              "description": "Комп’ютерне обладнанн",
              "scheme": "ДК021",
              "id": "30230000-0"
            },
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ],
            "deliveryAddress": {
              "streetAddress": "вул. Банкова 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "79000",
              "countryName": "Україна"
            },
            "unit": {
              "name": "штук",
              "value": {
                "amount": 12.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87"
            }
          },
          {
            "id": "98b99c56dacf48728e1a069205bdf6c2",
            "description": "Комп’ютерне обладнання",
            "quantity": 5.0,
            "deliveryDate": {
              "startDate": "2023-10-12T01:00:00+03:00",
              "endDate": "2023-10-15T01:00:00+03:00"
            },
            "classification": {
              "description": "Комп’ютерне обладнанн",
              "scheme": "ДК021",
              "id": "30230000-0"
            },
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ],
            "deliveryAddress": {
              "streetAddress": "вул. Банкова 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "79000",
              "countryName": "Україна"
            },
            "unit": {
              "name": "штук",
              "value": {
                "amount": 6.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87"
            }
          }
        ],
        "value": {
          "amount": 230.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true,
          "amountNet": 223.0
        },
        "id": "eb4343b446004f47aa2ec7f6e542f196"
      }
    }


Conclusion
----------

Change can create both a buyer and a supplier.

Two fields will be added to `Change`: `modifications` - changes that will be applied after activation and `previousValues`: auto-generated field for storing history.

For activating `Change` buyer and supplier must sign this change by adding signature documents to the change.

After activating `Change` all modifications will be applied to the contract.
