.. _lot_deliveries:

Deliveries logic for lots
==========================

В цій секції описана логіка додавання умов поставки під майбутній контракт.

Структура об'єкта поставки (delivery)
---------------------------------------

В рамках лоту може бути одна поставка, хоча предметів закупівлі більше ніж один, а також декілька поставок, хоча предмет закупівлі закуповується лише один.

Об'єкт delivery буде знаходитися на рівні лоту. Це буде поле `deliveries` - масив об'єктів.

Delivery
--------

:id:
    uid, auto-generated

    Id of delivery

:expectedTerms:
    string, required

    Тип очікування поставки.
    Замовник обов'язково повинен обрати коли він очікує поставку.
    Можливі значення:

    * `afterContractSigning` - після підписання контракту
    * `afterPrepayment` - після отримання авансу
    * `afterApplicationReceiving` - після отримання заявки
    * `daily` - щоденно
    * `monthly` - щомісячно

:description:
    string

    Опис поставки.
    Можна вказати додатковий опис поставки, наприклад до якого числа кожного місяця треба поставити товар.

:duration:
    :ref:`deliveryDuration` object, required

    Строк поставки

:addresses:
    List of :ref:`deliveryAddress` objects

    Адрес в рамках однієї поставки може бути декілька, це означатиме, що замовник не може вирішити куди саме наразі потрібно і вказує всі варіанти, які в нього є, щоб постачальник міг порахувати вартість пропозиції

    Це може бути як загальна адреса: Україна, так і список областей, або одна область в якій працює замовник.
    Також замовник може вказати конкретну адресу з вулицею, містом, областю, країною та поштовим індексом

:quantity:
    integer

    Кількість предмету закупівлі у поставці

    Замовник може вказати конкретну кількість предмету закупівлі у лоті під поставку.
    Якщо кількість невизначена і про це буде повідомлено у заявці - це поле буде пустим.

:relatesTo:
    string, required

    Type of related element.
    Possible values are:

    * `lot`
    * `item`

:relatedItem:
    string, required

    The id of related element.


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


.. _deliveryAddress:

Address
-------

:streetAddress:
    string

    The street address. For example, вул. Ярослава Мудрого 15.

:locality:
    string

    The locality. For example, Mountain View.

:region:
    string

    The region. For example, Київська область.

:postalCode:
    string

    The postal code. For example, 94043.

:countryName:
    string, multilingual, required

    The country name. For example, Україна.


Delivery POST
-------------

Додати умови поставки можна через лот.

Приклад №1: 100 Кетаміну в Київську область 14 днів після підписання контракту

.. sourcecode:: http

    POST /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "expectedTerms": "afterContractSigning",
        "duration": {
            "days": 14,
            "type": "working",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Київська область",
        }],
        "quantity": 100,
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua//api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries/2328f66eebf04c4497d0fb223feeb0er

    {
      "data": {
        "id": "2328f66eebf04c4497d0fb223feeb0er",
        "expectedTerms": "afterContractSigning",
        "duration": {
            "days": 14,
            "type": "working",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Київська область",
        }],
        "quantity": 50,
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
        "dateCreated": "2024-01-01T11:11:0000",
    }


Приклад №2: 50 Кетаміну та 50 Аспіріну в Житомирську область 14 днів після підписання контракту

Це буде два запити POST

.. sourcecode:: http

    POST /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "expectedTerms": "afterContractSigning",
        "duration": {
            "days": 14,
            "type": "working",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Житомирська область",
        }],
        "quantity": 50,
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
      }
    }

    POST /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "expectedTerms": "afterContractSigning",
        "duration": {
            "days": 14,
            "type": "working",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Житомирська область",
        }],
        "quantity": 50,
        "relatesTo": "item",
        "relatedItem": "00ss3344556677889900qqwweerrqq11",
      }
    }

Подивимося на поставки в лоті:

.. sourcecode:: http

    GET /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua


    HTTP/1.0 200 OK
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua//api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries/2328f66eebf04c4497d0fb223feeb0er

    {
      "data": [{
        "id": "2328f66eebf04c4497d0fb223feeb0er",
        "expectedTerms": "afterContractSigning",
        "duration": {
            "days": 14,
            "type": "working",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Житомирська область",
        }],
        "quantity": 50,
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
        "dateCreated": "2024-01-01T11:11:0000"
    },{
        "id": "re28f66eebf04c4497d0fb223feeb211",
        "expectedTerms": "afterContractSigning",
        "duration": {
            "days": 14,
            "type": "working",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Житомирська область",
        }],
        "quantity": 50,
        "relatesTo": "item",
        "relatedItem": "00ss3344556677889900qqwweerrqq11",
        "dateCreated": "2024-01-01T11:20:0000",
    }]

Приклад №3: Замовник може вказати, що кількість поставки невизначена і про це буде повідомлено у заявці:

.. sourcecode:: http

    POST /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "expectedTerms": "afterApplicationReceiving",
        "duration": {
            "days": 10,
            "type": "calendar",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Харківська область",
            "streetAddress": "вул. Героїв Харкова 104",
        }],
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua//api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries/2328f66eebf04c4497d0fb223feeb0er

    {
      "data": {
        "id": "2328f66eebf04c4497d0fb223feeb0er",
        "expectedTerms": "afterApplicationReceiving",
        "duration": {
            "days": 10,
            "type": "calendar",
        },
        "addresses": [{
            "country": "Україна",
            "region": "Харківська область",
            "streetAddress": "вул. Героїв Харкова 104",
        }],
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
        "dateCreated": "2024-01-01T11:11:0000",
    }

Приклад №4: Адрес в рамках однієї поставки може бути декілька, це означатиме, що замовник не може вирішити куди саме наразі потрібно і вказує всі варіанти, які в нього є, щоб постачальник міг порахувати вартість пропозиції

.. sourcecode:: http

    POST /api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "expectedTerms": "afterApplicationReceiving",
        "duration": {
            "days": 10,
            "type": "calendar",
        },
        "quantity": 15,
        "addresses": [{
            "country": "Україна",
            "region": "Харківська область",
        }, {
            "country": "Україна",
            "region": "Житомирська область",
        }, {
            "country": "Україна",
            "region": "Київська область",
        }],
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua//api/2.5/tenders/4178f66eebf04c4497d0fb223feeb0fe/lots/222333222111qwd111ccc111aaaq12/deliveries/2328f66eebf04c4497d0fb223feeb0er

    {
      "data": {
        "id": "2328f66eebf04c4497d0fb223feeb0er",
        "expectedTerms": "afterPrepayment",
        "duration": {
            "days": 10,
            "type": "calendar",
        },
        "quantity": 15,
        "addresses": [{
            "country": "Україна",
            "region": "Харківська область",
        }, {
            "country": "Україна",
            "region": "Житомирська область",
        }, {
            "country": "Україна",
            "region": "Київська область",
        }],
        "relatesTo": "item",
        "relatedItem": "11223344556677889900qqwweerrttyy",
        "dateCreated": "2024-01-01T11:11:0000",
    }
