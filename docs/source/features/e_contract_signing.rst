Підписання електронного контракту
=================================


Скоуп функціональності
----------------------

Цей документ покриває базовий функціонал підпису електронного контракту замовником і постачальником.
Нижче буде описаний механізм взаємодії майданчиків з АПІ ЦБД для реалізації даного процесу.

Процес Awarding відбувається на майданчику закупівель,
а Contracting - на майданчику документообігу.


.. image:: img/e_contract_signing/activity.png


Шина обміну - фід контрактів
----------------------------

АПІ ЦБД виступає посередником між майдинчиками.
На діаграмі нижче помазаний приклад інтеграції і взаємодії між учасниками процесу.

.. image:: img/e_contract_signing/sequence.png


Майданчики користуються фідом по контрактам, щоб підтягнути оновлення.
Фід дозволяє усі сторонам "бачити" апдейти як тільки ті внесені в ЦБД.

.. sourcecode:: http

    GET /api/2.5/contracts?opt_fields=status HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
        "data": [
            {
                "status": "pending",
                "dateModified": "2024-05-12T08:27:55.026619+03:00",
                "id": "d5b73ce2bdc3426a86871a99a6cffcb6"
            },
            {
                "dateModified": "2024-05-12T07:45:08.834444+03:00",
                "status": "active",
                "id": "509fe127752a41fab9304a33623e507d"
            },
            {
                "dateModified": "2024-05-12T06:08:25.195462+03:00",
                "status": "active",
                "id": "9863d4377e7b4721b1ae02d8f4be08d9"
            },
        ],
        "next_page": {
            "offset": 1715446569.779,
            "path": "/api/2.5/contracts?descending=1&opt_fields=status&offset=1715446569.779",
            "uri": "https://public.api.openprocurement.org/api/2.5/contracts?descending=1&opt_fields=status&offset=1715446569.779"
        },
        "prev_page": {
            "offset": 1715491675.028,
            "path": "/api/2.5/contracts?opt_fields=status&offset=1715491675.028",
            "uri": "https://public.api.openprocurement.org/api/2.5/contracts?opt_fields=status&offset=1715491675.028"
        }
    }


Допоки контракт формуєтся автоматично, читання фіду контрактів буде достатньо
для імплементації процессу підписання.


**Важливо**: Скоріш за все майданчикам буде краще "запам'ятовувати" усі контракти з фіду,
оскільки клієнт (замовник чи постачальник) може зареєструватися на їх платформі пізніше.




Внесення в процедуру інформації необхідної для підписання контракта
-------------------------------------------------------------------


Замовник надає інформацію про підписанта
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Замовник має додати інформацію про підписанта, а саме:

- ПІБ підписанта
- Посада підписанта
- Імейл підписанта
- Телефон підписанта
- Реквізити організації (ІБАН)


Замовник передає інформацію про підписанта контракта щe :ref:`на етапі планування закупівлі <planning_tutorial>`.
Це потрібно для того, щоб на момент визначення переможця вся необхідня для контракту інформація вже була в системі.

Реалізовано буде через передачу :ref:`SignerInfo <SignerInfo>` в buyers ref:`об'єкт плану <plan>`.


.. sourcecode:: http

    POST /api/2.5/plans HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "procuringEntity": {
          "identifier": {
            "scheme": "UA-EDR",
            "id": "111983",
            "legalName": "ДП Державне Управління Справами"
          },
          "name": "ДУС",
          "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1"
          },
          "kind": "general"
        },
        "buyers": [
          {
            "name": "Школяр",
            "identifier": {
              "scheme": "UA-EDR",
              "id": "00137256",
              "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
              "uri": "http://www.sc.gov.ua/"
            },
            "address": {
              "streetAddress": "вул. Островського, 33",
              "locality": "м. Вінниця",
              "region": "Вінницька область",
              "postalCode": "21100",
              "countryName": "Україна"
            },
            "signerInfo": {
                "name": "Test Testovich",
                "email": "example@email.com",
                "telephone": "+380950000000",
                "iban": "111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
            },
            "kind": "general"
          }
        ],
        ...
      }
    }



Постачальник надає інформацію про підписанта
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Постачальник надає інформацію про підписанта контракта ще на етапі подачі пропозиції.
Це може виглядати, наприклад, наступним чином:

.. sourcecode:: http

    POST /api/2.5/tenders/3f5ff57c43ca4ba6b3a1d0619b7a14c3/bids HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "tenderers": [
          {
            "name": "ДКП «Школяр»",
            "address": {
              "countryName": "Україна",
              "locality": "м. Вінниця",
              "postalCode": "21100",
              "region": "Вінницька область",
              "streetAddress": "вул. Островського, 33"
            },
            "contactPoint": {
              "email": "soleksuk@gmail.com",
              "name": "Сергій Олексюк",
              "telephone": "+380432216930"
            },
            "identifier": {
              "scheme": "UA-EDR",
              "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
              "id": "00137256",
              "uri": "http://www.sc.gov.ua/"
            },
            "signer_info": {
                "name": "Дмитро Гендір",
                "email": "d.gendir@email.com",
                "telephone": "+380950000000",
                "iban": "UA111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
            },
            "scale": "micro"
          }
        ],
        "status": "draft",
        "items": [...],
        "lotValues": [...]
      }


Тобто разом з пропозицією подається і інформація про підписанта можливого контракту.



Відображення контракта - Замовник
---------------------------------

.. raw:: html

    <style> .orange {color:orange} </style>
    <style> .red {color:red} </style>


.. role:: orange
.. role:: red


:orange:`Тріггер №1: Поява pending контракта`



Майданчику необхідно відобразити замовнику "попередній перегляд майбутнього контракту".
Перейти до роботи з ним можна буде після закінчення періоду оскарження рішення про переможця.


Майданчик отримає попередньо заповнену інформацію контракту від апі


.. sourcecode:: http

    GET /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5 HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "awardID": "c220713cbd024586b6382ef97a852dc7",
        "contractID": "UA-2023-10-10-000001-a-1",
        "contractTemplateName": "00000000-0.0001.01",
        "author": null,
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
            "signer_info": {
                "name": "Дмитро Гендір",
                "email": "d.gendir@email.com",
                "telephone": "+380950000000",
                "iban": "UA111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
            },
            "scale": "micro"
          }
        ],
        "owner": "broker",
        "tender_id": "fd45af80ad9f4574994f7f6254012693",
        "items": [
          {
            "id": "a23a71262ac642b88f2fdb69011d74b1",
            "description": "Комп’ютерне обладнання",
            "quantity": 5.0,
            "classification": {
              "description": "Cartons",
              "scheme": "ДК021",
              "id": "44617100-9"
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
            "deliveryDate": {
              "startDate": "2023-10-12T01:00:00+03:00",
              "endDate": "2023-10-15T01:00:00+03:00"
            },
            "unit": {
              "name": "кг",
              "value": {
                "amount": 6.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "KGM"
            }
          },
          {
            "id": "c8f30df33ae14c65b38931d68e63d757",
            "description": "Комп’ютерне обладнання",
            "quantity": 5.0,
            "classification": {
              "description": "Cartons",
              "scheme": "ДК021",
              "id": "44617100-9"
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
            "deliveryDate": {
              "startDate": "2023-10-12T01:00:00+03:00",
              "endDate": "2023-10-15T01:00:00+03:00"
            },
            "unit": {
              "name": "кг",
              "value": {
                "amount": 6.0,
                "currency": "UAH",
                "valueAddedTaxIncluded": true
              },
              "code": "KGM"
            }
          }
        ],
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
                "iban": "111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
           },
          "kind": "general"
        },
        "value": {
          "amount": 500.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true,
          "amountNet": 500.0
        },
        "bid_owner": "broker",
        "status": "pending",
        "dateCreated": "2023-10-10T01:00:00+03:00",
        "dateModified": "2023-10-10T01:00:00+03:00",
        "id": "c503bd32d67b4bb895fe50cce285bac5"
      },
      "config": {
        "restricted": false
      }
    }


З відповіді майданчик підтягує наступні поля (структурa :ref:`Contract`):

1. Інформація по контракту:
    Загальні відомості про контракт

    - До якого тендеру належить контракт (ідентифікатор) - не редагується - **tender_id**
    - Вартість контракту і ПДВ - не редагується - **value**

2. Інформація про предмет закупівлі - **items**
    - Опис предмету закупвлі - редагується - **items.description**
    - Класифікація предмету закупівлі по коду ДК - не редагується - **items.classification**
    - Додаткова класифікація предмету закупівлі, якщо існує - не редагується - **items.additionalClassifications**
    - Адрес поставки - не редагується - **items.deliveryAddress**
    - Дата поставки (паралельна розробка) - **items.deliveryDate**
    - Характеристики предмету закупівлі - **items.attributes**

        - Назва характеристики - **items.attributes.name**
        - Значення характеристики - **items.attributes.values**
        - Одиниця виміру характеристики  - **items.attributes.unit**

    - Кількість предмету закупівлі - не редагується - **items.quantity**
    - Одиниця виміру предмету закупівлі - не редагується - **items.unit**

3. Інформація по замовнику - **buyer**
    - Ідентифікатор організації (ЕДРПОУ) - не редагується - **buyer.identifier**
    - Назва організації - не редагується - **buyer.name**, **buyer.name_en**
    - Адреса організації - не редагується - **buyer.address**

4. Інформація по постачальнику - **suppliers**
    - Ідентифікатор організації (ЕДРПОУ) - не редагується - **suppliers.identifier**
    - Назва організації - не редагується - **suppliers.name**
    - Адреса організації - не редагується - **suppliers.address**

5. Інформація про шаблон контракту **contractTemplateName**



Підписання "електронних полів" контракту
----------------------------------------

Для файлу підпису використовується конверт з даними - тобто в одному файлі `sign.p7s`
зберігаються і підпис і "електронні поля" в форматі json.


Підпис на "електронні поля" контракту накладаються паралельно усіма сторонами і завантажуються в апі.


Замовник підписує "Елетронні поля"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Приклад завантаження від імені від замовника:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "sign.p7s",
        "documentType": "signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=y%2Bc%2FV%2BSIqnf36NvLLrimQyaWUtCCEZEgtEl%2FsALE5XH5bqEoXwnwNhAkhsKg1JfVY9%2BEwvXxHKhaD5p%2BZBhCBw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents/16c04af53eb1469ea9b4bfdb4d26a1d1

    {
      "data": {
        "id": "16c04af53eb1469ea9b4bfdb4d26a1d1",
        "hash": "md5:00000000000000000000000000000000",
        "title": "sign.p7s",
        "documentType": "signature",
        "author": "buyer",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
        "datePublished": "2023-10-10T03:00:00+03:00",
        "dateModified": "2023-10-10T03:00:00+03:00"
      }
    }



:orange:`Тріггер №2: Поява в контракті підпису замовника`
При появі підпису замовника,
майданчик має проінформувати свого користувача (постачальника) про це.



Постачальник підписує "Елетронні поля"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Приклад завантаження від імені від постачальника:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents?acc_token=1b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "sign.p7s",
        "documentType": "signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5b3b7a2ee860772dcdc649ca1705e69f?Signature=y%2Bc%2FV%2BSIqnf36NvLLrimQyaWUtCCEZEgtEl%2FsALE5XH5bqEoXwnwNhAkhsKg1JfVY9%2BEwvXxHKhaD5p%2BZBhCBw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents/16c04af53eb1469ea9b4bfdb4d26a1d2

    {
      "data": {
        "id": "16c04af53eb1469ea9b4bfdb4d26a1d2",
        "hash": "md5:00000000000000000000000000000000",
        "title": "sign.p7s",
        "documentType": "signature",
        "author": "supplier",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5b3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
        "datePublished": "2023-10-10T03:00:00+03:00",
        "dateModified": "2023-10-10T03:00:00+03:00"
      }
    }




:orange:`Тріггер №3: Поява в контракті підпису постачальника`
При появі підпису замовника,
майданчик має проінформувати свого користувача (замовника) про це.


"Елетронні поля" підписані усіма
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Коли і постачальник і замовник додали свої підписи, контракт в апі може виглядати десь так:

(тут поки без підписів "електронних полів")


.. sourcecode:: http

    GET /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5 HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
          "id":"c503bd32d67b4bb895fe50cce285bac5",
          "status":"pending",
          "documents":[
             {
                "id": "16c04af53eb1469ea9b4bfdb4d26a1d1",
                "hash": "md5:00000000000000000000000000000000",
                "title": "sign.p7s",
                "documentType": "signature",
                "author": "buyer",
                "format": "application/pkcs7-signature",
                "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "datePublished": "2023-10-10T03:00:00+03:00",
                "dateModified": "2023-10-10T03:00:00+03:00"
             },
             {
                "id": "16c04af53eb1469ea9b4bfdb4d26a1d2",
                "hash": "md5:00000000000000000000000000000000",
                "title": "sign.p7s",
                "documentType": "signature",
                "author": "supplier",
                "format": "application/pkcs7-signature",
                "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5b3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "datePublished": "2023-10-10T03:00:00+03:00",
                "dateModified": "2023-10-10T03:00:00+03:00"
             }
          ],
          ...
       },
       "config":{
          "restricted":false
       }
    }




Підписання документу контракта (Опціонально)
--------------------------------------------

:red:`TBD: pdf документ не погоджено`

Може бути зроблено одночасно через підписання і "електроних полів" контракту і самого контракта.


Створення файла контракта
~~~~~~~~~~~~~~~~~~~~~~~~~

Коли вся інформація в контракті заповнена, можна створити документ контракта і почати процесс підписання.


В апі ЦБД має бути завантажено файл контакту:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "contract.pdf",
        "documentType": "contractSigned",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/1ea9c5fa82c84b2a8206318bc86360df?Signature=y%2Bc%2FV%2BSIqnf36NvLLrimQyaWUtCCEZEgtEl%2FsALE5XH5bqEoXwnwNhAkhsKg1JfVY9%2BEwvXxHKhaD5p%2BZBhCBw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pdf"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents/08682b48035643a39d924df55eb915e0

    {
      "data": {
        "id": "08682b48035643a39d924df55eb915e0",
        "hash": "md5:00000000000000000000000000000000",
        "title": "contract.pdf",
        "documentType": "contractSigned",
        "format": "application/pdf",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/1ea9c5fa82c84b2a8206318bc86360df?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
        "documentOf": "contract",
        "datePublished": "2023-10-10T01:00:00+03:00",
        "dateModified": "2023-10-10T01:00:00+03:00"
      }
    }


Замовник підписує контракт
~~~~~~~~~~~~~~~~~~~~~~~~~~

Замовник накладає підпис на файл і підпис додається в апі:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "sign.p7s",
        "documentType": "signature",
        "documentOf": "contractDocument",
        "relatedItem": "08682b48035643a39d924df55eb915e0",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=y%2Bc%2FV%2BSIqnf36NvLLrimQyaWUtCCEZEgtEl%2FsALE5XH5bqEoXwnwNhAkhsKg1JfVY9%2BEwvXxHKhaD5p%2BZBhCBw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents/16c04af53eb1469ea9b4bfdb4d26a1de

    {
      "data": {
        "id": "16c04af53eb1469ea9b4bfdb4d26a1de",
        "hash": "md5:00000000000000000000000000000000",
        "title": "sign.p7s",
        "documentType": "signature",
        "documentOf": "contractDocument",
        "relatedItem": "08682b48035643a39d924df55eb915e0",
        "author": "buyer",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
        "datePublished": "2023-10-10T03:00:00+03:00",
        "dateModified": "2023-10-10T03:00:00+03:00"
      }
    }


Постачальник підписує контракт
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Користувач накладає ЕЦП, майданчик передає в апі відповідний файл:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "sign.p7s",
        "documentType": "signature",
        "documentOf": "contractDocument",
        "relatedItem": "08682b48035643a39d924df55eb915e0",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/1ea9c5fa82c84b2a8206318bc86360df?Signature=y%2Bc%2FV%2BSIqnf36NvLLrimQyaWUtCCEZEgtEl%2FsALE5XH5bqEoXwnwNhAkhsKg1JfVY9%2BEwvXxHKhaD5p%2BZBhCBw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/documents/08682b48035643a39d924df55eb915e0

    {
      "data": {
        "id": "9438d93a59264568b75f95c5de5c8d9b",
        "hash": "md5:00000000000000000000000000000000",
        "title": "sign.p7s",
        "documentType": "signature",
        "documentOf": "contractDocument",
        "relatedItem": "08682b48035643a39d924df55eb915e0",
        "author": "supplier",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/1ea9c5fa82c84b2a8206318bc86360df?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
        "datePublished": "2023-10-10T02:00:00+03:00",
        "dateModified": "2023-10-10T02:00:00+03:00"
      }
    }


Як результат ми маємо:
 - "contract.pdf" з типом "contractSigned"
 - "sign.p7s" з типом "signature" та полями documentOf+relatedItem, що посилаються на "contract.pdf"

Можна програмно визначити, чи є контракт підписаний постачальником, бо у файла підписа вказано `"author": "supplier"`.



Контракт підписаний усіма
~~~~~~~~~~~~~~~~~~~~~~~~~

Коли і постачальник і замовник додали свої підписи, контракт в апі може виглядати десь так:

(тут поки без підписів "електронних полів")


.. sourcecode:: http

    GET /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5 HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
          "id":"c503bd32d67b4bb895fe50cce285bac5",
          "status":"pending",
          "documents":[
             {
                "id":"08682b48035643a39d924df55eb915e0",
                "hash":"md5:00000000000000000000000000000000",
                "title":"contract.pdf",
                "documentType":"contractSigned",
                "format":"application/pdf",
                "url":"http://public-docs-sandbox.prozorro.gov.ua/get/1ea9c5fa82c84b2a8206318bc86360df?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "documentOf":"contract",
                "datePublished":"2023-10-10T01:00:00+03:00",
                "dateModified":"2023-10-10T01:00:00+03:00"
             },
             {
                "id":"9438d93a59264568b75f95c5de5c8d9b",
                "hash":"md5:00000000000000000000000000000000",
                "title":"sign.p7s",
                "documentType":"signature",
                "documentOf":"contractDocument",
                "relatedItem":"08682b48035643a39d924df55eb915e0",
                "author":"supplier",
                "format":"application/pkcs7-signature",
                "url":"http://public-docs-sandbox.prozorro.gov.ua/get/1ea9c5fa82c84b2a8206318bc86360df?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "datePublished":"2023-10-10T02:00:00+03:00",
                "dateModified":"2023-10-10T02:00:00+03:00"
             },
             {
                "id":"16c04af53eb1469ea9b4bfdb4d26a1de",
                "hash":"md5:00000000000000000000000000000000",
                "title":"sign.p7s",
                "documentType":"signature",
                "documentOf":"contractDocument",
                "relatedItem":"08682b48035643a39d924df55eb915e0",
                "author":"buyer",
                "format":"application/pkcs7-signature",
                "url":"http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "datePublished":"2023-10-10T03:00:00+03:00",
                "dateModified":"2023-10-10T03:00:00+03:00"
             }
          ],
          ...
       },
       "config":{
          "restricted":false
       }
    }



Скасування контракту з постачальником
-------------------------------------

І замовник і постачальник можуть опублікувати рішення про "скасування підписання".
У будь-якому випадку відмова від підписання буде зупиняти поточний процес контрактингу і починати новий.

Стандарти будуть включати базовий перелік типів відмов.


Приклад стандарту

.. sourcecode:: json

    {
        "outOfStock": {
            "title_uk": "відсутність товарів, можливості виконання робіт і послуг",
            "title_en": "lack of goods, the possibility of performing works and services"
        },
        "requireChanges": {
            "title_uk": "необхідність внести зміни до контракту",
            "title_en": "the need to amend the contract"
        }
    }



Ініціація скасування підписання через відсутність товарів
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

У випадку відмови з таким типом, замовник публікує "скасування підписання".
Після чого замовник може переглянути своє рішення про переможця. Поточний контракт буде скасовано через скасування рішення про пеерможця.

Користувач обирає тип причини `outOfStock` та вказує його в полі `reasonType`:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/cancellations?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "reason": "бананів немає 😔",
        "reasonType": "outOfStock"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/cancellations/16c04af53eb1469ea9b4bfdb4d26a1da

    {
      "data": {
        "id": "16c04af53eb1469ea9b4bfdb4d26a1da",
        "status": "pending"
        "author": "supplier",
        "dateCreated": "2023-10-10T03:00:00+03:00",
        "reason": "бананів немає 😔",
        "reasonType": "outOfStock"
      }
    }


Додавання документів до скасування відбувається ідентично з іншими cancellations в системі.
Результуючий контракт має в собі інформацію про скасування, але залишається в `pending`:


.. sourcecode:: http

    GET /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5 HTTP/1.0

    Host: public-api-sandbox.prozorro.gov.ua
    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
          "awardID": "c220713cbd024586b6382ef97a852dc7",
          "contractID": "UA-2023-10-10-000001-a-1",
          "contractTemplateName": "00000000-0.0001.01",
          "author": null,
          "status": "pending",
          "cancellations": [
             {
                "id": "16c04af53eb1469ea9b4bfdb4d26a1da",
                "status": "pending"
                "author": "supplier",
                "dateCreated": "2023-10-10T03:00:00+03:00",
                "datePublished": "2023-10-10T04:00:00+03:00",
                "reason": "бананів немає 😔",
                "reasonType": "outOfStock"
                "documents": [
                  {
                    "hash": "md5:00000000000000000000000000000000",
                    "title": "Notice.pdf",
                    "format": "application/pdf",
                    "url": "http://public-docs-sandbox.prozorro.gov.ua/get/20d128e9e0d94b378f0d20eff02ff88a?Signature=QS7hf8dU8Isr0Gx2mdwGuwjLDNmtMoB5LiUhr9Tr9YS6ojYM4GK8efB0rqFu%2FXzy7Uma7Qi50c5nWl%2BFVfzqDQ%3D%3D&KeyID=a8968c46",
                    "language": "uk",
                    "id": "3a864a9e9fda4374af78d5f9831fb9f7",
                    "datePublished": "2023-10-16T01:15:06+03:00",
                    "dateModified": "2023-10-16T01:15:06+03:00"
                  }
                ]
              }
          ],
          ...
       }
       ...
    }


:orange:`Тріггер №4: Поява в контракті повідомлення про скасування через відсутність товару`
При появі скасування, майданчик може повідомити замовника про скасування контракта.


Скасування контракт процесу з даним постачальником
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Замовник може :ref:`відмінити своє рішення про переможця<econtracting_tutorial_cancelling_award>`
і почати контратинг з насутпним постачальником.


:orange:`Тріггер №5: Контракт переходить в cancelled і нова версія контракту має іншого постачальника`
При зміні рішення про переможця, майданчик може повідомити постачальника про цю визначну подію



Оновлення інформації в контракті
--------------------------------


Ініціація скасування підписання через необхідність змін
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Користувач обирає тип причини `requireChanges` та вказує його в полі `reasonType`:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/cancellations?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "reason": "Необхідно змінити підписанта постачальника",
        "reasonType": "requireChanges"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/cancellations/16c04af53eb1469ea9b4bfdb4d26a1da

    {
      "data": {
        "id": "16c04af53eb1469ea9b4bfdb4d26a1da",
        "status": "pending"
        "author": "supplier",
        "dateCreated": "2023-10-10T03:00:00+03:00",
        "reason": "Необхідно змінити підписанта постачальника",
        "reasonType": "requireChanges"
      }
    }


:orange:`Тріггер №6: Поява в контракті повідомлення про скасування через необхідність змін`
Майданчик може повідомити інших підписантів про намір учасника створити оновлену версію контракту.



Публікація нової версії контракту
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо ці дані контракту не підходять для підписання контракту,
то замовник (або постачальник) зможе оновити її,
але **тільки після скасування актуальної версії контракту**.

Ініціатор робить зміни до електроних полів, після чого майданчик публікує нову версію контракту.
Нова версія контракту буде створеня додатковим полем  `"author": "supplier"` або `"author": "supplier"`,
відповідно до ініціатора скасування:


.. sourcecode:: http

    POST /api/2.5/contracts HTTP/1.0
    Host: api-sandbox.prozorro.gov.ua

    {
      "data": {
        "tender_id": "fd45af80ad9f4574994f7f6254012693",
        "awardID": "c220713cbd024586b6382ef97a852dc7",
        "contractTemplateName": "00000000-0.0001.01",
        "items": [...],
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
            "signer_info": {
                "name": "Дмитро Гендір",
                "email": "d.gendir@email.com",
                "telephone": "+380950000000",
                "iban": "UA111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
            },
            "scale": "micro"
          }
        ],
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
          "signer_info": {
            "name": "Test Testovich",
            "telephone": "+380950000000",
            "email": "example@email.com",
            "iban": "UA111111111111111",
            "authorizedBy": "Статут компанії",
            "position": "Генеральний директор"
          },
          "kind": "general"
        },
        "value": {
          "amount": 500.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true,
          "amountNet": 500.0
        }
      },
      "config": {
        ...
      }
    }

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "tender_id": "fd45af80ad9f4574994f7f6254012693",
        "awardID": "c220713cbd024586b6382ef97a852dc7",
        "contractID": "UA-2023-10-10-000002-a-1",
        "contractTemplateName": "00000000-0.0001.01",
        "author": "supplier",
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
            "signer_info": {
                "name": "Дмитро Гендір",
                "email": "d.gendir@email.com",
                "telephone": "+380950000000",
                "iban": "UA111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
            },
            "scale": "micro"
          }
        ],
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
          "signer_info": {
            "name": "Test Testovich",
            "telephone": "+380950000000",
            "email": "example@email.com",
            "iban": "UA111111111111111",
            "authorizedBy": "Статут компанії",
            "position": "Генеральний директор"
          },
          "kind": "general"
        },
        "value": {
          "amount": 1500.0,
          "currency": "UAH",
          "valueAddedTaxIncluded": true,
          "amountNet": 1500.0
        },
        "status": "pending",
        "dateCreated": "2023-11-11T01:00:00+03:00",
        "dateModified": "2023-11-11T01:00:00+03:00",
        "id": "d503bd32d67b4bb895fe50cce285bac5",
        ...
      },
      "config": {
        ...
      }
    }


- Створення нового контракта можливо лише за умови скасування попереднього.
- Одночасно існує тільки одна версія pending контракту
- Якщо обидві сторони одночасно намагаються створити нову версію, то переможе найшвидший 🏃


:orange:`Тріггер №7: Поява нового контракту + відмін попереднього`
Майданчик через фід побачить перехід в cancelled статус першого контракту і новий об'єкт контракту.
Має повідомити про це підписантів.

Також усі наявні контракти можна подивитись через ендпоінт контрактів тендера:


.. sourcecode:: http

    POST /api/2.5/tenders/fd45af80ad9f4574994f7f6254012693/contracts HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    {
        "data": [
            {
                "id": "c503bd32d67b4bb895fe50cce285bac5",
                "status": "cancelled",
                "awardID": "c220713cbd024586b6382ef97a852dc7",
                "contractID": "UA-2023-10-10-000001-a-1",
                "date": "2023-10-10T01:00:00+03:00",
                "value": {
                    "amount": 500.0,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": true,
                    "amountNet": 500.0
                }
            },
            {
                "id": "d503bd32d67b4bb895fe50cce285bac5",
                "status": "pending",
                "awardID": "c220713cbd024586b6382ef97a852dc7",
                "contractID": "UA-2023-10-10-000001-a-2",
                "date": "2023-10-11T01:00:00+03:00",
                "value": {
                    "amount": 1500.0,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": true,
                    "amountNet": 1500.0
                }
            }
        ]
    }




Додаткові угоди
---------------

Зміни до контрактів вносяться через :ref:`додаткові угоди<econtract_change_updated_flow>`



Авторизація користувачів з різних майданчиків
----------------------------------------------

Для додавання даних в ЦБД, майданчку треба буде дозвіл на такі дії.
Зараз надання дозволу надаєтся за токеном тендера. Це не спрацює,
якщо користувачі працюють з тендером на одному майданчику, а з контрактом - на іншому.

Усі перевірки ЕЦП, телефонів, імейлів робить саме майданчик.

ЦБД повертає токени доступу до об'єктів, як правило, тим майданчикам, з яких було створено конкретний об'єкт.
Але від цього можна відійти, і для контрактів видавати токен першому майданчику, з якого користувач забажав працювати з конкретним контрактом.

Як це має виглядати

.. image:: img/e_contract_signing/simple_sequence.png

Таким чином ми зберігаємо можливість кожному користувачу/стороні контраку обирати
де, вони будуть працювати з контрактом.
І так само гарантуєм, що два майданчики одночасно не працюють від імені одного користувача з одним об'єктом.


:orange:`Важливо: Майданчики мають отримувати токен лише на запит користувача.`


Механізм складаєтся з двох кроків для підтримки :ref:`2pc` (read `more <https://en.wikipedia.org/wiki/Two-phase_commit_protocol>`_)
Тому реалізація апі буде виглядати як два запити:

.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/access HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    {
       "data":{
         "identifier":{
            "scheme":"UA-EDR",
            "id":"00037256",
         }
      }
    }

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
         "identifier":{
            "scheme":"UA-EDR",
            "id":"00037256",
         },
         "active": False,
      },
      "access": {
        "token": "d449625b66ae44b0a591b8551cfd1bfe",
        "transfer": "da2cfe17ad6546cc910d2b3750b2830c"
      }
    }


.. sourcecode:: http

    PUT /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/access?acc_token=d449625b66ae44b0a591b8551cfd1bfe HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    {
       "data":{
        "identifier":{
            "scheme":"UA-EDR",
            "id":"00037256",
         },
         "active": True,
      }
    }

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
         "identifier":{
            "scheme":"UA-EDR",
            "id":"00037256",
         },
         "active": True,
      }
    }



*Плюси*:
 - Простий механізм, не потрібно взаємодій між майданчиками.

*Мінуси*
 - При неправільній імпліментації керування може отримувати або неправильний користувач, або неочікуваний для користувача майданчик
