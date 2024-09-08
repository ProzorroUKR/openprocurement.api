.. _econtract_change_updated_flow:

Додаткові угоди (зміни) в EContract
===================================

Зміни в умови контрактів можуть бути внесені підписантами через подання і підписання додаткових угод.
В системі використовується термінологія "змін" / "changes".



Передумови
----------

Зміни можна вносити в підписані контракти:


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
             "signerInfo": {
                "name": "Test Testovich",
                "email": "example@email.com",
                "telephone": "+380950000000",
                "iban": "234234234234234",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
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
          "status": "active",
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


Створення пропозиції змін / документу доп. угоди
------------------------------------------------

Ініціатором внесення змін може бути обидва замовник і постачальник


Ініціатор заповнює три обов'язкових поля:

:rationale:
    string, причина змін

:rationaleTypes:
    list, типи причин

:modifications:
    object, нові значення в електронних полях


`modifications` це структура, що відображає зміни в електроних поля, які буде внесено:

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


Запит створення пропозиції змін:

.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0

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
        "author": "supplier",
        "status": "pending",
        "date": "2023-10-10T01:00:00+03:00"
      }
    }


Створення документу доп. угоди
------------------------------


Коли об'єкт зміни створено в системі ініціатор може створити документ доп. угоди і почати процес підписання.
Спершу в систему завантажується сам документ угоди

.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31/documents?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0

    Authorization: Bearer broker
    Content-Length: 333
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "documentType": "contractChangeSigned",
        "title": "dop-1.pdf",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=mFBbg4SYLP%2BQk4Cn6xwFtFp2XKpLLLIQmIqKvBsiciOF6nuiH7Gw9Wmk0IsPpNVvMLNn21PDO0c5XMfjxxX5Dw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pdf"
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31/documents/32ec55c6c6144f7a8fceea1ed68a5290

    {
      "data": {
        "documentType": "contractChangeSigned",
        "hash": "md5:00000000000000000000000000000000",
        "title": "dop-1.pdf",
        "format": "application/pdf",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=cG1JU%2F1r%2B2jlQbXxJsq3HCYzzTi9mderkkqPwomMk34J6oAJ%2B7GRNC3kUgPO3zskbNjKkMkhiaJY2PmkUlOkBA%3D%3D&KeyID=a8968c46",
        "id": "32ec55c6c6144f7a8fceea1ed68a5290",
        "datePublished": "2024-10-10T01:00:00+03:00",
        "dateModified": "2024-10-10T01:00:00+03:00"
      }
    }


Передати на підписання
----------------------


Ініціатор угоди після завантаження, може підписати її першим або передати на підписання другому учаснику.
Другий учасник угоди має бути проінформаваний майданчиком про підписану доп. угоду першим учасником
або про факт передачі йому на підписання.

Щоб передати зміни на підписання, робиться наступний запит до апі:

.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31/submits?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "recipient": "buyer",
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31/submits/26c04af63eb1469ea9b4bfdb4d26a1dd

    {
      "data": {
        "id": "26c04af63eb1469ea9b4bfdb4d26a1dd",
        "recipient": "buyer",
        "author": "supplier",
        "datePublished": "2024-10-10T03:00:00+03:00"
      }
    }


Підписання доп. угоди
---------------------


Зміни може бути "застосовано" після підписання угоди усіма сторонами.
Для підписання треба накласти ЕЦП на pdf доп. угоди та завантажити файл в АПІ:

.. sourcecode:: http

    POST /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31/documents?acc_token=3b095197e5f94f76a28bae3a3079c206 HTTP/1.0

    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "sign.p7s",
        "documentType": "signature",
        "documentOf": "contractChangeDocument",
        "relatedItem": "32ec55c6c6144f7a8fceea1ed68a5290",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=y%2Bc%2FV%2BSIqnf36NvLLrimQyaWUtCCEZEgtEl%2FsALE5XH5bqEoXwnwNhAkhsKg1JfVY9%2BEwvXxHKhaD5p%2BZBhCBw%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "application/pkcs7-signature"
      }
    }

    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31/documents/26c04af53eb1469ea9b4bfdb4d26a1de

    {
      "data": {
        "id": "26c04af53eb1469ea9b4bfdb4d26a1de",
        "hash": "md5:00000000000000000000000000000000",
        "title": "sign.p7s",
        "documentType": "signature",
        "documentOf": "contractChangeDocument",
        "relatedItem": "32ec55c6c6144f7a8fceea1ed68a5290",
        "author": "buyer",
        "format": "application/pkcs7-signature",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
        "datePublished": "2024-10-10T03:00:00+03:00",
        "dateModified": "2024-10-10T03:00:00+03:00"
      }
    }


Активація змін до контракта
---------------------------

Активація змін може бути автоматичною / вимагати явної дії від ініціатора / будь-якої сторони,
в момент коли всі учасники наклали підписи:


.. sourcecode:: http

    PATCH /api/2.5/contracts/c503bd32d67b4bb895fe50cce285bac5/changes/b9887678ba3c448b977467c0fe3ada31?acc_token=1981a3b3a85d4159aabe55f5be082fd5 HTTP/1.0

    Authorization: Bearer broker
    Content-Length: 73
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active"
      }
    }


    HTTP/1.0 200 OK
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
        "author": "supplier",
        "status": "active",
        "date": "2024-11-10T01:00:00+03:00",
        "submits": [
            {
                "id": "26c04af63eb1469ea9b4bfdb4d26a1dd",
                "recipient": "buyer",
                "author": "supplier",
                "datePublished": "2024-10-10T03:00:00+03:00"
            }
        ],
        "documents": [
           {
                "documentType": "contractChangeSigned",
                "hash": "md5:00000000000000000000000000000000",
                "title": "dop-1.pdf",
                "format": "application/pdf",
                "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=cG1JU%2F1r%2B2jlQbXxJsq3HCYzzTi9mderkkqPwomMk34J6oAJ%2B7GRNC3kUgPO3zskbNjKkMkhiaJY2PmkUlOkBA%3D%3D&KeyID=a8968c46",
                "id": "32ec55c6c6144f7a8fceea1ed68a5290",
                "datePublished": "2024-10-10T01:00:00+03:00",
                "dateModified": "2024-10-10T01:00:00+03:00"
          },
          {
                "id": "26c04af53eb1469ea9b4bfdb4d26a1de",
                "hash": "md5:00000000000000000000000000000000",
                "title": "sign-1.p7s",
                "documentType": "signature",
                "documentOf": "contractChangeDocument",
                "relatedItem": "32ec55c6c6144f7a8fceea1ed68a5290",
                "author": "buyer",
                "format": "application/pkcs7-signature",
                "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "datePublished": "2024-10-11T03:00:00+03:00",
                "dateModified": "2024-10-11T03:00:00+03:00"
          },
          {
                "id": "36c04af53eb1469ea9b4bfdb4d26a1de",
                "hash": "md5:00000000000000000000000000000000",
                "title": "sign-2.p7s",
                "documentType": "signature",
                "documentOf": "contractChangeDocument",
                "relatedItem": "32ec55c6c6144f7a8fceea1ed68a5290",
                "author": "supplier",
                "format": "application/pkcs7-signature",
                "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                "datePublished": "2024-10-12T03:00:00+03:00",
                "dateModified": "2024-10-12T03:00:00+03:00"
          }
        ]
      }
    }



Підписання додаткових угод не змінює електронні поля самого контракту.
Тобто якщо, наприклад, термін контракту було змінено доп. угодою, то в `changes` буде актуальне значення,
а в контракті - актуальне на момент підписання контракту.


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
             "signerInfo": {
                "name": "Test Testovich",
                "email": "example@email.com",
                "telephone": "+380950000000",
                "iban": "234234234234234",
                "position": "Генеральний директор",
                "authorizedBy": "Статут компанії"
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
          "status": "active",
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
          ],
          "changes": [
             {
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
                "author": "supplier",
                "status": "active",
                "date": "2024-11-10T01:00:00+03:00",
                "submits": [
                    {
                        "id": "26c04af63eb1469ea9b4bfdb4d26a1dd",
                        "recipient": "buyer",
                        "author": "supplier",
                        "datePublished": "2024-10-10T03:00:00+03:00"
                    }
                ],
                "documents": [
                   {
                        "documentType": "contractChangeSigned",
                        "hash": "md5:00000000000000000000000000000000",
                        "title": "dop-1.pdf",
                        "format": "application/pdf",
                        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/34862599de094db7a8c9c37996ea4847?Signature=cG1JU%2F1r%2B2jlQbXxJsq3HCYzzTi9mderkkqPwomMk34J6oAJ%2B7GRNC3kUgPO3zskbNjKkMkhiaJY2PmkUlOkBA%3D%3D&KeyID=a8968c46",
                        "id": "32ec55c6c6144f7a8fceea1ed68a5290",
                        "datePublished": "2024-10-10T01:00:00+03:00",
                        "dateModified": "2024-10-10T01:00:00+03:00"
                  },
                  {
                        "id": "26c04af53eb1469ea9b4bfdb4d26a1de",
                        "hash": "md5:00000000000000000000000000000000",
                        "title": "sign-1.p7s",
                        "documentType": "signature",
                        "documentOf": "contractChangeDocument",
                        "relatedItem": "32ec55c6c6144f7a8fceea1ed68a5290",
                        "author": "buyer",
                        "format": "application/pkcs7-signature",
                        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                        "datePublished": "2024-10-11T03:00:00+03:00",
                        "dateModified": "2024-10-11T03:00:00+03:00"
                  },
                  {
                        "id": "36c04af53eb1469ea9b4bfdb4d26a1de",
                        "hash": "md5:00000000000000000000000000000000",
                        "title": "sign-2.p7s",
                        "documentType": "signature",
                        "documentOf": "contractChangeDocument",
                        "relatedItem": "32ec55c6c6144f7a8fceea1ed68a5290",
                        "author": "supplier",
                        "format": "application/pkcs7-signature",
                        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/5a3b7a2ee860772dcdc649ca1705e69f?Signature=x6tzZwzV4d5DGLeiqvD%2Bm0EdAUGgzUmYnoQ4AjImnxjQRU49JnE3aq50UHtPUVvIRfF5JSrLqmyF3tssHOT%2BCA%3D%3D&KeyID=a8968c46",
                        "datePublished": "2024-10-12T03:00:00+03:00",
                        "dateModified": "2024-10-12T03:00:00+03:00"
                  }
                ]
             }
          ]
       },
       "config":{
          "restricted":false
       }
    }
