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

Замовник має додати інформацію про підписанта
---------------------------------------------

Замовник має додати інформацію про підписанта, а саме:

- ПІБ підписанта
- Посада підписанта
- Імейл підписанта
- Телефон підписанта
- Реквізити організації (ІБАН)


.. sourcecode:: http

    PUT /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/buyer/signer_info?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "name": "Test Testovich",
        "telephone": "+380950000000",
        "email": "example@email.com",
        "iban": "UA111111111111111",
        "authorizedBy": "Статут компанії",
        "position": "Генеральний директор"
      }
    }


    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "name": "Test Testovich",
        "email": "example@email.com",
        "telephone": "+380950000000",
        "iban": "UA111111111111111",
        "position": "Генеральний директор",
        "authorizedBy": "Статут компанії"
      }
    }


Постачальник надає інформацію про підписанта
--------------------------------------------

Постачальник надає інформацію про підписанта контракта ще на етапі подачі пропозиції.
Це може виглядати, наприклад, наступним чином:

.. sourcecode:: http

    POST /api/2.5/tenders/3f5ff57c43ca4ba6b3a1d0619b7a14c3/bids HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "contract": {
            "signer_info": {
                "name": "Дмитро Гендір",
                "email": "d.gendir@email.com",
                "telephone": "+380950000000",
                "iban": "UA111111111111111",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
            }
        },
        "tenderers": [
          {
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
            "name": "ДКП «Школяр»",
            "scale": "micro"
          }
        ],
        "status": "draft",
        "items": [],
        "lotValues": []
      }


Тобто разом з пропозицією подається і інформація про підписанта можливого контракту.




Замовник оновлює інформацію про підписанта постачальника
--------------------------------------------------------

Інформація надана ще на етапі пропозиції може бути неактуальною і замовник може її оновити:


.. sourcecode:: http

    PUT /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/suppliers/signer_info?acc_token=e83ced17c21845f6b06d197ccd74988d HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "name": "Ухват Підписенко",
        "email": "u.pidpis@email.com",
        "telephone": "+380950000001",
        "iban": "UA111111111111111",
        "position": "Замгендір по підписам",
        "authorizedBy": "Магічна мушля"
      }
    }

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "name": "Ухват Підписенко",
        "email": "u.pidpis@email.com",
        "telephone": "+380950000001",
        "iban": "UA111111111111111",
        "position": "Замгендір по підписам",
        "authorizedBy": "Магічна мушля"
      }
    }



Замовник створює файл контракта
-------------------------------

Коли вся інформація в контракті заповнена, можна створити документ контракта і почати процесс підписання.

:red:`TBD: pdf документ із темлейта може створюватись на майданчиках або централізовано - в апі.`


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
--------------------------

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



:orange:`Тріггер №2: Поява в контракті підпису постачальника`
При появі підпису замовника, постачальник також зможе підписувати контракт.
Майданчик має проінформувати свого користувача про це.



Замовник не підписує, а передає постачальнику на підписання першому
-------------------------------------------------------------------

Якщо постачальник обирає таку опцію, це також передається в апі, наприклад:

.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/submits?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "recipient": "supplier",
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/submits/26c04af63eb1469ea9b4bfdb4d26a1dd

    {
      "data": {
        "id": "26c04af63eb1469ea9b4bfdb4d26a1dd",
        "recipient": "supplier",
        "author": "buyer",
        "datePublished": "2023-10-10T03:00:00+03:00"
      }
    }


:orange:`Тріггер №3: Поява ознаки по "передання" документу`
В такому випадку постачальник має підписувати контракт,
а майданчик має проінформувати користувача про це.



Постачальник підписує контракт
------------------------------

Незалежно від того хто підписує перший, процес накладання не відрізняється.
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



:orange:`Тріггер №4: Поява в контракті підпису постачальника`
Якщо в апі з'явився підпис постачальника, але ше немає підписа замовника,
то майданчик замовника має проінформувати користувача про це.



Контракт підписаний усіма
-------------------------

Коли і постачальник і замовник додали свої підписи, контракт в апі може виглядати десь так:


.. sourcecode:: http

    GET /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5 HTTP/1.0
    Host: public-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
          "awardID":"c220713cbd024586b6382ef97a852dc7",
          "contractID":"UA-2023-10-10-000001-a-1",
          "contractTemplateName": "00000000-0.0001.01",
          "suppliers":[
             {
                "name":"Державне управління справами",
                "identifier":{
                   "scheme":"UA-EDR",
                   "id":"00037256",
                   "uri":"http://www.dus.gov.ua/"
                },
                "address":{
                   "streetAddress":"вул. Банкова, 11, корпус 1",
                   "locality":"м. Київ",
                   "region":"м. Київ",
                   "postalCode":"01220",
                   "countryName":"Україна"
                },
                "scale":"micro"
             }
          ],
          "owner":"broker",
          "tender_id":"fd45af80ad9f4574994f7f6254012693",
          "items":[
             {
                "id":"a23a71262ac642b88f2fdb69011d74b1",
                "description":"Комп’ютерне обладнання",
                "quantity":5.0,
                "classification":{
                   "description":"Cartons",
                   "scheme":"ДК021",
                   "id":"44617100-9"
                },
                "additionalClassifications":[
                   {
                      "scheme":"INN",
                      "id":"17.21.1",
                      "description":"папір і картон гофровані, паперова й картонна тара"
                   }
                ],
                "deliveryAddress":{
                   "streetAddress":"вул. Банкова 1",
                   "locality":"м. Київ",
                   "region":"м. Київ",
                   "postalCode":"79000",
                   "countryName":"Україна"
                },
                "deliveryDate":{
                   "startDate":"2023-10-12T01:00:00+03:00",
                   "endDate":"2023-10-15T01:00:00+03:00"
                },
                "unit":{
                   "name":"кг",
                   "value":{
                      "amount":6.0,
                      "currency":"UAH",
                      "valueAddedTaxIncluded":true
                   },
                   "code":"KGM"
                }
             }
          ],
          "buyer":{
             "name":"Державне управління справами",
             "identifier":{
                "scheme":"UA-EDR",
                "id":"00037256",
                "uri":"http://www.dus.gov.ua/"
             },
             "address":{
                "streetAddress":"вул. Банкова, 11, корпус 1",
                "locality":"м. Київ",
                "region":"м. Київ",
                "postalCode":"01220",
                "countryName":"Україна"
             },
             "kind":"general"
          },
          "value":{
             "amount":500.0,
             "currency":"UAH",
             "valueAddedTaxIncluded":true,
             "amountNet":500.0
          },
          "bid_owner":"broker",
          "status":"pending",
          "dateCreated":"2023-10-10T01:00:00+03:00",
          "dateModified":"2023-10-10T01:00:00+03:00",
          "id":"c503bd32d67b4bb895fe50cce285bac5",
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
          ]
       },
       "config":{
          "restricted":false
       }
    }



Відхилення підписання
---------------------

Постачальник може опублікувати рішення про "відхилення підписання".
У будь-якому випадку відмова від підписання буде зупиняти поточний процес контрактингу і починати новий.

Чи буде новий процес проводитись з цим самим замовником чи ні, залежать від причини відмови.
Стандарти будуть включати базовий перелік типів відмов з ознакою чи є цей тип відмови таким,
що виключає можливість продовження контрактингу з цим постачальником.
Приклад стандарту

.. sourcecode:: json

    {
        "outOfStock": {
            "stops_contracting": true,
            "title_uk": "відсутність товарів, можливості виконання робіт і послуг",
            "title_en": "lack of goods, the possibility of performing works and services"
        },
        "contractChangesRequest": {
            "stops_contracting": false,
            "title_uk": "необхідність виправити деталі контракту",
            "title_en": "the need to correct the details of the contract"
        },
        "otherCanNotContinueContracting": {
            "stops_contracting": true,
            "title_uk": "інша причина, що унеможливлює подальшу участь у тендері",
            "title_en": "another reason that makes further participation in the tender impossible"
        },
        "otherCanContinueContracting": {
            "stops_contracting": false,
            "title_uk": "неможливість підписати цю версію контракту",
            "title_en": "inability to sign this version of the contract"
        }
    }


користувач обирає тип причини та вказує його в полі `reasonType`:


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
        "status": "draft"
        "author": "supplier",
        "dateCreated": "2023-10-10T03:00:00+03:00",
        "reason": "бананів немає 😔",
        "reasonType": "outOfStock"
      }
    }


Додавання документів до відхилення та зміна статусу відбувається ідентично з іншими cancellations в системі.


Контракт з "відхиленнями"


.. sourcecode:: http

    GET /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5 HTTP/1.0

    Host: public-api-sandbox.prozorro.gov.ua
    HTTP/1.0 200 OK
    Content-Type: application/json

    {
       "data":{
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
                  },
                  {
                    "hash": "md5:00000000000000000000000000000000",
                    "title": "signature.p7s",
                    "format": "application/p7s",
                    "url": "http://public-docs-sandbox.prozorro.gov.ua/get/32d128e9e0d94b378f0d20eff02ff18a?Signature=QS7hf8dU8Isr0Gx2mdwGuwjLDNmtMoB5LiUhr9Tr9YS6ojYM4GK8efB0rqFu%2FXzy7Uma7Qi50c5nWl%2BFVfzqDQ%3D%3D&KeyID=a8968c46",
                    "id": "4a864a9e9fda4374af78d5f9831fb9fa",
                    "datePublished": "2023-10-16T01:15:06+03:00",
                    "dateModified": "2023-10-16T01:15:06+03:00"
                  },
                ]
              }
          ],
          "awardID":"c220713cbd024586b6382ef97a852dc7",
          "contractID":"UA-2023-10-10-000001-a-1",
          "contractTemplateName": "00000000-0.0001.01",
          "suppliers":[
             {
                "name":"Державне управління справами",
                "identifier":{
                   "scheme":"UA-EDR",
                   "id":"00037256",
                   "uri":"http://www.dus.gov.ua/"
                },
                "address":{
                   "streetAddress":"вул. Банкова, 11, корпус 1",
                   "locality":"м. Київ",
                   "region":"м. Київ",
                   "postalCode":"01220",
                   "countryName":"Україна"
                },
                "scale":"micro"
             }
          ],
          "owner":"broker",
          "tender_id":"fd45af80ad9f4574994f7f6254012693",
          "items":[
             {
                "id":"a23a71262ac642b88f2fdb69011d74b1",
                "description":"Комп’ютерне обладнання",
                "quantity":5.0,
                "classification":{
                   "description":"Cartons",
                   "scheme":"ДК021",
                   "id":"44617100-9"
                },
                "additionalClassifications":[
                   {
                      "scheme":"INN",
                      "id":"17.21.1",
                      "description":"папір і картон гофровані, паперова й картонна тара"
                   }
                ],
                "deliveryAddress":{
                   "streetAddress":"вул. Банкова 1",
                   "locality":"м. Київ",
                   "region":"м. Київ",
                   "postalCode":"79000",
                   "countryName":"Україна"
                },
                "deliveryDate":{
                   "startDate":"2023-10-12T01:00:00+03:00",
                   "endDate":"2023-10-15T01:00:00+03:00"
                },
                "unit":{
                   "name":"кг",
                   "value":{
                      "amount":6.0,
                      "currency":"UAH",
                      "valueAddedTaxIncluded":true
                   },
                   "code":"KGM"
                }
             }
          ],
          "buyer":{
             "name":"Державне управління справами",
             "identifier":{
                "scheme":"UA-EDR",
                "id":"00037256",
                "uri":"http://www.dus.gov.ua/"
             },
             "address":{
                "streetAddress":"вул. Банкова, 11, корпус 1",
                "locality":"м. Київ",
                "region":"м. Київ",
                "postalCode":"01220",
                "countryName":"Україна"
             },
             "kind":"general"
          },
          "value":{
             "amount":500.0,
             "currency":"UAH",
             "valueAddedTaxIncluded":true,
             "amountNet":500.0
          },
          "bid_owner":"broker",
          "status":"pending",
          "dateCreated":"2023-10-10T01:00:00+03:00",
          "dateModified":"2023-10-10T01:00:00+03:00",
          "id":"c503bd32d67b4bb895fe50cce285bac5"
       },
       "config":{
          "restricted":false
       }
    }



:orange:`Тріггер №5: Поява в контракті повідомлення про відхилення`
При появі відхилення, майданчик замовника має повідомити його про це


Замовник підтверджує відхилення
-------------------------------

Після відхилення постачальником підписання,
замовник може :ref:`відмінити своє рішення про переможця<econtracting_tutorial_cancelling_award>`
і почати контратинг з насутпним постачальником.


Або, якщо можливо внести правки і підписати новий контракт з цим постачальником,
замовник підтверджує відміну поточного контракту і процес "заповнення-створення-підписання" почанється спочатку:


.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/cancellations?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/cancellations/16c04af53eb1469ea9b4bfdb4d26a1da

    {
      "data": {
        "id": "16c04af53eb1469ea9b4bfdb4d26a1da",
        "status": "active"
        "author": "supplier",
        "dateCreated": "2023-10-10T03:00:00+03:00",
        "reason": "бананів немає 😔",
        "reasonType": "outOfStock"
      }
    }


Авторизація користувачів з різних майданчиків
----------------------------------------------

Для додавання даних в ЦБД, майданчку треба буде дозвіл на такі дії.
Зараз надання дозволу надаєтся за токеном тендера. Це не спрацює,
якщо користувачі працюють з тендером на одному майданчику, а з контрактом - на іншому.


Передача авторизації через Relocation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

В ЦБД вже є варіант механізму "передачі" авторизації з майданчика на майданчик https://prozorro-api-docs.readthedocs.io/uk/master/relocation/contracts.html#example-for-contract

Ось як він може виглядати на діаграмі

.. image:: img/e_contract_signing/transfer_sequence.png


Його можна допрацювати / спростити для зручності/можливості використання:
 - Дозволити переносити кортакти в статусі pending
 - Приймати transfer токен не тільки контракта, а й тендера, щоб опціонально прибрати перший крок для майданчика 1
 - Зробити напівавтоматичну "передачу" transfer токена від одного майданчика до іншого


*Плюси*:
 - Механізм забезпечує необхідну ступінь авторизації,  вже є частиною ЦБД і вкладаєтся в загальну архітектуру.

*Мінуси*
 - Представники майданчиків висловились, що схема надто складна. Майже ніхто не реалізовував механізм relocation, тому це додаткова розробка.


Найбільш простий варіант, що тим не менш базується на токенах
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Механізм автентифікації та авторизації кінцевих користувачів завжди був делегований на майданчики.
Усі перевірки ЕЦП, телефонів, імейлів робить саме майданчик.

ЦБД повертає токени доступу до об'єктів, як правило, тим майданчикам, з яких було створено конкретний об'єкт.
Але від цього можна відійти, і для контрактів видавати токен першому майданчику, з якого користувач забажав працювати з конкретним контрактом.

Як це має виглядати

.. image:: img/e_contract_signing/simple_sequence.png

Таким чином ми зберігаємо можливість кожному користувачу/стороні контраку обирати
де, вони будуть працювати з контрактом.
Але так само гарантуєм, що два майданчики одночасно не працюють від імені одного користувача з одним об'єктом.


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
