.. _lot_deliveries:

Deliveries logic for lots
==========================

В цій секції описана логіка додавання умов поставки під майбутній контракт.

Структура об'єкта поставки
----------------------------

Умови поставки будуть зповнюватися використовуючи об'єкти `milestones` і `items` на рівні тендеру.

В об'єктах `items` буде вказано який саме предмет закупівлі, в якій кількості і по якій адресі його треба доставляти.
Якщо треба один і той самий предмет закупівлі доставляти на різні адреси і різну кількість - треба створити декілька `items` для кожної умови.

В об'єктах `milestones` буде вказано на який саме лот створена умова поставки, title до неї, можливо додатковий опис і строк поставки в днях.
Тип таких `milestones` буде `delivery`.

Milestone (delivery)
---------------------

:id:
    uid, auto-generated

:title:
    string, required

    Possible values will be set in dictionary.

    Тип очікування поставки.

    Замовник обов'язково повинен обрати коли він очікує поставку.

    Значення заповнюються згідно з `milestones <https://prozorroukr.github.io/standards/codelists/milestones/title.json>`__ довідниками.

:description:
    string

    Опис поставки.
    Можна вказати додатковий опис поставки, наприклад до якого числа кожного місяця треба поставити товар.

:type:
    string, required

    The only possible value for deliveries is:

    * `delivery`

:code:
    string, required

    Значення заповнюються згідно з `milestones <https://prozorroukr.github.io/standards/codelists/milestones/code.json>`_ довідниками.

:percentage:
    float, 0..100

    Sum of all tender (or lot) milestones should be 100

:duration:
    :ref:`deliveryDuration` object, required

    Строк поставки

:sequenceNumber:
    integer, required, non negative

:relatedLot:
    uid

    Id of related :ref:`lot`.

.. _deliveryDuration:

Duration
--------

:days:
    integer, required, positive

:type:
    string, required

    Possible values are:

    * `working`
    * `banking`
    * `calendar`


Delivery Logic
--------------

Додати умови поставки можна через лот, item та milestone.

Приклад №1: 100 Кетаміну в Київську область 14 днів після підписання контракту

При створенні тендеру треба вказати предмет закупівлі Кетамін в кількості 100 штук з заповненим `deliveryAddress` в Київську область.
Після цього додати лот до тендеру і змінити в `item` поле `relatedLot` з посиланням на доданий лот.
Тепер до тендеру необхідно додати `milestone` з типом `delivery` з посиланням на доданий лот  `relatedLot`, вказавши тип і строк поставки.

.. sourcecode:: http

    PATCH /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe HTTP/1.0

    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "milestones": [
          {
            "title": "signingTheContract",
            "code": "standard",
            "type": "delivery",
            "duration": {
              "days": 14,
              "type": "calendar"
            },
            "sequenceNumber": 1,
            "percentage": 100,
            "relatedLot": "222333222111qwd111ccc111aaaq12",
          }
        ],
        "items": [
          {
            "id": "4bb51392e7724e88b10b312453ac7db9",
            "description": "Пігулки",
            "unit": {
              "name": "кетамін",
              "value": {
                "amount": 10.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87",
            },
            "quantity": 100.0,
            "classification": {
              "description": "Фармацевтична продукція",
              "scheme": "ДК021",
              "id":  "33600000-6",
            },
            "relatedLot": "222333222111qwd111ccc111aaaq12",
            "deliveryAddress": {
              "region": "Київська область",
              "countryName": "Україна"
            }
          }
        ]
      }
    }


    HTTP/1.0 200 OK
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua//api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe

    {
      "data": {
        ...,
        "milestones": [
          {
            "id": "2328f66eebf04c4497d0fb223feeb0er",
            "title": "signingTheContract",
            "code": "standard",
            "type": "delivery",
            "duration": {
              "days": 14,
              "type": "calendar"
            },
            "sequenceNumber": 1,
            "percentage": 100,
            "relatedLot": "222333222111qwd111ccc111aaaq12",
          }
        ],
        "items": [
          {
            "id": "4bb51392e7724e88b10b312453ac7db9",
            "description": "Пігулки",
            "unit": {
              "name": "кетамін",
              "value": {
                "amount": 10.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87",
            },
            "quantity": 100.0,
            "classification": {
              "description": "Фармацевтична продукція",
              "scheme": "ДК021",
              "id":  "33600000-6",
            },
            "relatedLot": "222333222111qwd111ccc111aaaq12",
            "deliveryAddress": {
              "region": "Київська область",
              "countryName": "Україна"
            }
          }
        ]
      }
    }


Приклад №2: 50 Кетаміну та 50 Аспіріну в Житомирську область 14 днів після підписання контракту

Це буде два різних предмета закупівлі але одна умова поставки для всього лоту:

.. sourcecode:: http

    PATCH /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe HTTP/1.0

    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "milestones": [
          {
            "title": "signingTheContract",
            "code": "standard",
            "type": "delivery",
            "duration": {
              "days": 14,
              "type": "calendar"
            },
            "sequenceNumber": 1,
            "percentage": 100,
            "relatedLot": "222333222111qwd111ccc111aaaq12",
          }
        ],
        "items": [
          {
            "id": "4bb51392e7724e88b10b312453ac7db9",
            "description": "Пігулки",
            "unit": {
              "name": "кетамін",
              "value": {
                "amount": 10.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87",
            },
            "quantity": 50.0,
            "classification": {
              "description": "Фармацевтична продукція",
              "scheme": "ДК021",
              "id":  "33600000-6",
            },
            "relatedLot": "222333222111qwd111ccc111aaaq12",
            "deliveryAddress": {
              "region": "Житомирська область",
              "countryName": "Україна"
            }
          }, {
            "id": "00b51392e7724e88b10b312453ac7d66",
            "description": "Пігулки",
            "unit": {
              "name": "аспірин",
              "value": {
                "amount": 10.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87",
            },
            "quantity": 50.0,
            "classification": {
              "description": "Фармацевтична продукція",
              "scheme": "ДК021",
              "id":  "33600000-6",
            },
            "relatedLot": "222333222111qwd111ccc111aaaq12",
            "deliveryAddress": {
              "region": "Житомирська область",
              "countryName": "Україна"
            }
          }
        ]
      }
    }

    HTTP/1.0 200 OK
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua//api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe

    {
      "data": {
        ...,
        "milestones": [
          {
            "id": "2328f66eebf04c4497d0fb223feeb0er",
            "title": "signingTheContract",
            "code": "standard",
            "type": "delivery",
            "duration": {
              "days": 14,
              "type": "calendar"
            },
            "sequenceNumber": 1,
            "percentage": 100,
            "relatedLot": "222333222111qwd111ccc111aaaq12",
          }
        ],
        "items": [
          {
            "id": "4bb51392e7724e88b10b312453ac7db9",
            "description": "Пігулки",
            "unit": {
              "name": "кетамін",
              "value": {
                "amount": 10.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87",
            },
            "quantity": 50.0,
            "classification": {
              "description": "Фармацевтична продукція",
              "scheme": "ДК021",
              "id":  "33600000-6",
            },
            "relatedLot": "222333222111qwd111ccc111aaaq12",
            "deliveryAddress": {
              "region": "Житомирська область",
              "countryName": "Україна"
            }
          }, {
            "id": "00b51392e7724e88b10b312453ac7d66",
            "description": "Пігулки",
            "unit": {
              "name": "аспірин",
              "value": {
                "amount": 10.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "H87",
            },
            "quantity": 50.0,
            "classification": {
              "description": "Фармацевтична продукція",
              "scheme": "ДК021",
              "id":  "33600000-6",
            },
            "relatedLot": "222333222111qwd111ccc111aaaq12",
            "deliveryAddress": {
              "region": "Житомирська область",
              "countryName": "Україна"
            }
          }
        ]
      }
    }
