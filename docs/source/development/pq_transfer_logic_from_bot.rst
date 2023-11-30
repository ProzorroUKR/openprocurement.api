.. _pq_transfer_logic_from_bot:

Transfer logic from PQ bot to CBD
=================================


This section describes the logic of refusal of the priceQuotationBot and transferring validations from the bot to the CBD during tender activation.

Creating tender
---------------

Tender creation remains unchanged for PQ. A tender is created in the same way as before in the status `draft`:

.. sourcecode:: http

    POST /api/2.5/tenders?opt_pretty=1 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 4542
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "Комп’ютерне обладнання",
        "mainProcurementCategory": "goods",
        "procuringEntity": {
          "name": "Державне управління справами",
          "identifier": {
            "scheme": "UA-EDR",
            "id": "00037256",
            "uri": "http://www.dus.gov.ua/"
          },
          "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1"
          },
          "contactPoint": {
            "name": "Державне управління справами",
            "telephone": "+0440000000"
          },
          "kind": "general"
        },
        "value": {
          "amount": 22000,
          "currency": "UAH"
        },
        "tenderPeriod": {
          "endDate": "2023-10-04T01:00:00+03:00"
        },
        "procurementMethodType": "priceQuotation",
        "procurementMethod": "selective",
        "items": [
          {
            "description": "Комп’ютерне обладнання",
            "quantity": 5,
            "deliveryDate": {
              "startDate": "2023-09-22T01:00:00+03:00",
              "endDate": "2023-09-25T01:00:00+03:00"
            },
            "unit": {
              "name": "кг",
              "code": "KGM",
              "value": {
                "amount": 6
              }
            },
            "deliveryAddress": {
              "countryName": "Україна",
              "postalCode": "79000",
              "region": "м. Київ",
              "locality": "м. Київ",
              "streetAddress": "вул. Банкова 1"
            },
            "classification": {
              "scheme": "ДК021",
              "id": "44617100-9",
              "description": "Cartons"
            },
            "profile": "655360-30230000-889652-40000777",
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ]
          }
        ],
        "agreement": {
          "id": "2e14a78a2074952d5a2d256c3c004dda"
        },
        "criteria": [
          {
            "description": "Форма випуску",
            "requirementGroups": [
              {
                "description": "Форма випуску",
                "requirements": [
                  {
                    "dataType": "string",
                    "expectedValue": "Розчин для інфузій",
                    "title": "Форма випуску"
                  }
                ]
              }
            ],
            "title": "Форма випуску"
          },
          {
            "description": "Доза діючої речовини",
            "requirementGroups": [
              {
                "description": "Доза діючої речовини",
                "requirements": [
                  {
                    "dataType": "integer",
                    "minValue": 5,
                    "title": "Доза діючої речовини",
                    "unit": {
                      "code": "KGM",
                      "name": "кілограми"
                    }
                  }
                ]
              }
            ],
            "title": "Доза діючої речовини"
          },
          {
            "description": "Форма випуску",
            "requirementGroups": [
              {
                "description": "Форма випуску",
                "requirements": [
                  {
                    "dataType": "string",
                    "expectedValues": [
                      "Відповідь1",
                      "Відповідь2",
                      "Відповідь3",
                      "Відповідь4"
                    ],
                    "expectedMinItems": 2,
                    "expectedMaxItems": 3,
                    "title": "Форма випуску"
                  }
                ]
              }
            ],
            "title": "Форма випуску"
          }
        ]
      },
      "config": {
        "hasAuction": false,
        "hasAwardingOrder": true,
        "hasValueRestriction": true,
        "valueCurrencyEquality": true,
        "hasPrequalification": false,
        "minBidsNumber": 1,
        "hasPreSelectionAgreement": true
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f

    {
      "data": {
        "mainProcurementCategory": "goods",
        "procurementMethod": "selective",
        "title": "Комп’ютерне обладнання",
        "procurementMethodType": "priceQuotation",
        "awardCriteria": "lowestCost",
        "status": "draft",
        "agreement": {
          "id": "2e14a78a2074952d5a2d256c3c004dda"
        },
        "value": {
          "amount": 22000.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true
        },
        "tenderPeriod": {
          "endDate": "2023-10-04T01:00:00+03:00",
          "startDate": "2023-09-20T01:00:00+03:00"
        },
        "procuringEntity": {
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
          "contactPoint": {
            "telephone": "+0440000000",
            "name": "Державне управління справами"
          },
          "kind": "general"
        },
        "items": [
          {
            "id": "6d463cf854bc4c0eb04915ba7c172bea",
            "description": "Комп’ютерне обладнання",
            "classification": {
              "description": "Cartons",
              "scheme": "ДК021",
              "id": "44617100-9"
            },
            "quantity": 5.0,
            "deliveryDate": {
              "startDate": "2023-09-22T01:00:00+03:00",
              "endDate": "2023-09-25T01:00:00+03:00"
            },
            "deliveryAddress": {
              "streetAddress": "вул. Банкова 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "79000",
              "countryName": "Україна"
            },
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ],
            "unit": {
              "name": "кг",
              "value": {
                "amount": 6.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "KGM"
            },
            "profile": "655360-30230000-889652-40000777"
          }
        ],
        "criteria": [
          {
            "id": "8cc74439d2954c768f5dcfb5cb05e7dc",
            "title": "Форма випуску",
            "description": "Форма випуску",
            "requirementGroups": [
              {
                "id": "f7534cb234fe46a2a30f0d69d7d10914",
                "description": "Форма випуску",
                "requirements": [
                  {
                    "id": "25ad302697704d249e9d653933f909ee",
                    "title": "Форма випуску",
                    "dataType": "string",
                    "expectedValue": "Розчин для інфузій"
                  }
                ]
              }
            ]
          },
          {
            "id": "e6f67e9363e646798af5218a387229af",
            "title": "Доза діючої речовини",
            "description": "Доза діючої речовини",
            "requirementGroups": [
              {
                "id": "cd0fab014c454a63aee04b3f154244f6",
                "description": "Доза діючої речовини",
                "requirements": [
                  {
                    "id": "d3cb95288b334796b1562a0c638e526b",
                    "title": "Доза діючої речовини",
                    "dataType": "integer",
                    "unit": {
                      "code": "KGM",
                      "name": "кілограми"
                    },
                    "minValue": 5
                  }
                ]
              }
            ]
          },
          {
            "id": "04c9bc91e999415dbe174b1605adb116",
            "title": "Форма випуску",
            "description": "Форма випуску",
            "requirementGroups": [
              {
                "id": "1336eff0d6df4ffb839bda177861dd2b",
                "description": "Форма випуску",
                "requirements": [
                  {
                    "id": "a917b3e240d94416aac128cd1c3775e1",
                    "title": "Форма випуску",
                    "dataType": "string",
                    "expectedValues": [
                      "Відповідь1",
                      "Відповідь2",
                      "Відповідь3",
                      "Відповідь4"
                    ],
                    "expectedMinItems": 2,
                    "expectedMaxItems": 3
                  }
                ]
              }
            ]
          }
        ],
        "tenderID": "UA-2023-09-20-000001-a",
        "owner": "broker",
        "date": "2023-09-20T01:00:00+03:00",
        "dateCreated": "2023-09-20T01:00:00+03:00",
        "dateModified": "2023-09-20T01:00:00+03:00",
        "id": "bb8949e735294cbaa864bd3bc68a1e5f"
      },
      "config": {
        "hasAuction": false,
        "hasAwardingOrder": true,
        "hasValueRestriction": true,
        "valueCurrencyEquality": true,
        "hasPrequalification": false,
        "minBidsNumber": 1,
        "hasPreSelectionAgreement": true
      },
      "access": {
        "token": "d3c6750ff65148df856b59e65feba396",
        "transfer": "310d898a127548d195e67ab4293aaa05"
      }
    }


Modifying tender
------------------

Procuring Entity can modify tender before activating.
In previous flow with PQ bot there was the same stage before publishing (before changing status to `draft.publishing`).


Activating tender
------------------

In previous flow after creation Procuring Entity published procedure by changing status to `draft.publishing` where **priceQuotationBot** robot ran validation of the procedure and supplemented procedure with additional data taken from ProZorro e-Catalogues database including `shortListedFirms`.

After successful validation priceQuotationBot transmitted procedure to status: `active.tendering` or `draft.unsuccessful` in case if procedure did not pass validation due to invalid options.

Now we transfer all robot's validation logic to CBD and check it while Procuring Entity is changing status to `active.tendering` by patching tender.

PQ robot validations:

* Existence of item profile in catalogue

* Existence of related agreement

* Equality of profile agreement and related agreement in tender

* Agreement should not be in terminated status

* Agreement has qualified suppliers


Possible errors
---------------

If Procuring Entity will try to activate PQ procedure with non-existed profile in catalogue, we will see error:

.. sourcecode:: http

    PATCH /api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f?acc_token=d3c6750ff65148df856b59e65feba396 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 40
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active.tendering"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "items.profile",
          "description": "Profile 655360-30230000-889652-40000777 not found in catalogue."
        }
      ]
    }

If Procuring Entity will try to activate PQ procedure with non-existed agreement, the next error will be generated:

.. sourcecode:: http

    PATCH /api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f?acc_token=d3c6750ff65148df856b59e65feba396 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 40
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active.tendering"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "agreement",
          "description": "Agreement not found by agreement_id 2e14a78a2074952d5a2d256c3c004dda"
        }
      ]
    }

In case profile agreement and related agreement in tender aren't equal, the next error will be generated:

.. sourcecode:: http

    PATCH /api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f?acc_token=d3c6750ff65148df856b59e65feba396 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 40
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active.tendering"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "agreement",
          "description": "Tender agreement doesn't match profile agreement"
        }
      ]
    }

If agreement is in terminated status:

.. sourcecode:: http

    PATCH /api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f?acc_token=d3c6750ff65148df856b59e65feba396 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 40
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active.tendering"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "agreement",
          "description": "Agreement 2e14a78a2074952d5a2d256c3c004dda not in active status"
        }
      ]
    }

In case agreement doesn't have qualified suppliers:

.. sourcecode:: http

    PATCH /api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f?acc_token=d3c6750ff65148df856b59e65feba396 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 40
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active.tendering"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "agreement",
          "description": "Agreement 2e14a78a2074952d5a2d256c3c004dda doesn't have qualified suppliers"
        }
      ]
    }

If there is problem with connection to ProZorro e-Catalogues, we will see error:

.. sourcecode:: http

    PATCH /api/2.5/tenders/bb8949e735294cbaa864bd3bc68a1e5f?acc_token=d3c6750ff65148df856b59e65feba396 HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 40
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active.tendering"
      }
    }


    HTTP/1.0 409 Conflict
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          "description": "Error while getting data from ProZorro e-Catalogues: Connection closed. Try again later"
        }
      ]
    }


Successful scenario
-------------------

If PQ procedure matches all requirements, it will be switched to `active.tendering` status and `shortListedFirms` will be added to procedure from ProZorro e-Catalogues database:

.. sourcecode:: http

    GET /api/2.5/tenders/511ad32c232540d693bcdda2dd603406 HTTP/1.0
    Authorization: Bearer broker
    Host: public-api-sandbox.prozorro.gov.ua


    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "date": "2023-09-20T01:00:00+03:00",
        "dateModified": "2023-09-20T01:00:00+03:00",
        "dateCreated": "2023-09-20T01:00:00+03:00",
        "tenderID": "UA-2023-09-20-000001-a",
        "owner": "broker",
        "title": "Комп’ютерне обладнання",
        "mainProcurementCategory": "goods",
        "procurementMethod": "selective",
        "procurementMethodType": "priceQuotation",
        "awardCriteria": "lowestCost",
        "status": "active.tendering",
        "agreement": {
          "id": "2e14a78a2074952d5a2d256c3c004dda"
        },
        "shortlistedFirms": [
          {
            "name": "Товариство з обмеженою відповідальністю «Пікселі»",
            "identifier": {
              "scheme": "UA-EDR",
              "id": "00037256",
              "legalName": "Товариство з обмеженою відповідальністю «Пікселі»"
            },
            "address": {
              "streetAddress": "бул.Дружби Народів, 8",
              "locality": "м.Київ",
              "region": "Київська область",
              "postalCode": "01100",
              "countryName": "Україна"
            },
            "contactPoint": {
              "email": "contact@pixel.pix",
              "telephone": "+0671234567",
              "name": "Оксана Піксель"
            },
            "scale": "large",
            "id": "UA-EDR-12345678",
            "status": "active"
          },
          {
            "name": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
            "identifier": {
              "scheme": "UA-EDR",
              "id": "87654321",
              "legalName": "Товариство з обмеженою відповідальністю «Штекер-Пекер»"
            },
            "address": {
              "streetAddress": "вул. Кластерна, 777-К",
              "locality": "м.Тернопіль",
              "region": "Тернопільська область",
              "postalCode": "46000",
              "countryName": "Україна"
            },
            "contactPoint": {
              "email": "info@shteker.pek",
              "telephone": "+0951234567",
              "name": "Олег Штекер"
            },
            "scale": "large",
            "id": "UA-EDR-87654321",
            "status": "active"
          }
        ],
        "value": {
          "amount": 22000.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true
        },
        "tenderPeriod": {
          "startDate": "2023-09-20T01:00:00+03:00",
          "endDate": "2023-10-04T01:00:00+03:00"
        },
        "procuringEntity": {
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
          "contactPoint": {
            "telephone": "+0440000000",
            "name": "Державне управління справами"
          },
          "kind": "general"
        },
        "noticePublicationDate": "2023-09-20T01:00:00+03:00",
        "items": [
          {
            "id": "1624a28ab11b43cabcaef9018c023a16",
            "description": "Комп’ютерне обладнання",
            "classification": {
              "description": "Cartons",
              "scheme": "ДК021",
              "id": "44617100-9"
            },
            "quantity": 5.0,
            "deliveryDate": {
              "startDate": "2023-09-22T01:00:00+03:00",
              "endDate": "2023-09-25T01:00:00+03:00"
            },
            "deliveryAddress": {
              "streetAddress": "вул. Банкова 1",
              "locality": "м. Київ",
              "region": "м. Київ",
              "postalCode": "79000",
              "countryName": "Україна"
            },
            "additionalClassifications": [
              {
                "scheme": "INN",
                "id": "17.21.1",
                "description": "папір і картон гофровані, паперова й картонна тара"
              }
            ],
            "unit": {
              "name": "кг",
              "value": {
                "amount": 6.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "KGM"
            },
            "profile": "655360-30230000-889652-40000777"
          }
        ],
        "criteria": [
          {
            "id": "fc286b057a6f4e90af906d671cabd8c4",
            "title": "Форма випуску",
            "description": "Форма випуску",
            "requirementGroups": [
              {
                "id": "94d7ddacdb7c4428872b19615e455e5c",
                "description": "Форма випуску",
                "requirements": [
                  {
                    "id": "eb40cc8ae615437cb0f97f4e4e584d14",
                    "title": "Форма випуску",
                    "dataType": "string",
                    "expectedValue": "Розчин для інфузій"
                  }
                ]
              }
            ]
          },
          {
            "id": "09832e562d6049089f1b2d6806e45a20",
            "title": "Доза діючої речовини",
            "description": "Доза діючої речовини",
            "requirementGroups": [
              {
                "id": "1de5131390d041a98c0333e4b1a5bd27",
                "description": "Доза діючої речовини",
                "requirements": [
                  {
                    "id": "3b6248539c3d4ff1a69d98d3f79a941e",
                    "title": "Доза діючої речовини",
                    "dataType": "integer",
                    "unit": {
                      "code": "KGM",
                      "name": "кілограми"
                    },
                    "minValue": 5
                  }
                ]
              }
            ]
          },
          {
            "id": "52aa71c7eee743f18b0d05ea705e76aa",
            "title": "Форма випуску",
            "description": "Форма випуску",
            "requirementGroups": [
              {
                "id": "76232039d4ce4994824d26510f0bf484",
                "description": "Форма випуску",
                "requirements": [
                  {
                    "id": "e75acce3b5eb403ca05b2428c5f7592f",
                    "title": "Форма випуску",
                    "dataType": "string",
                    "expectedValues": [
                      "Відповідь1",
                      "Відповідь2",
                      "Відповідь3",
                      "Відповідь4"
                    ],
                    "expectedMinItems": 2,
                    "expectedMaxItems": 3
                  }
                ]
              }
            ]
          }
        ],
        "contractTemplateName": "00000000-0.0001.01",
        "next_check": "2023-10-04T01:00:00+03:00",
        "id": "bb8949e735294cbaa864bd3bc68a1e5f"
      },
      "config": {
        "hasAuction": false,
        "hasAwardingOrder": true,
        "hasValueRestriction": true,
        "valueCurrencyEquality": true,
        "hasPrequalification": false,
        "minBidsNumber": 1,
        "hasPreSelectionAgreement": true
      }
    }


Conclusion
----------

PQ procedure will not have statuses `draft.publishing`, `draft.unsuccessful` anymore.

If PQ procedure doesn't match all requirements, it won't be switched to `active.tendering` until all requirements is met.

Logic of creation and modification of PQ procedure won't be changed.

Next steps after `active.tendering` status stays the same.
