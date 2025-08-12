.. _modify_framework_period:

Історичність внесення змін терміну дії відборів
================================================

Під час активації відборів система перевіряє максимально та мінімально допустимий термін тривалості відборів.

* Мінімально допустимий термін тривалості - 365 днів.

* Максимально допустимий термін тривалості - 1461 день.

Якщо активувати відбор з терміном тривалості менше 365 днів, то побачимо помилку:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "qualificationPeriod": {
          "startDate": "2025-03-07T00:00:00+02:00",
          "endDate": "2026-01-01T00:00:00+02:00"
        },
        "status": "active"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          "description": "qualificationPeriod must be at least 365 full calendar days long"
        }
      ]
    }

Якщо активувати відбор з терміном тривалості більше 1461 день, то побачимо помилку:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "qualificationPeriod": {
          "startDate": "2025-03-07T00:00:00+02:00",
          "endDate": "2029-06-01T00:00:00+02:00"
        },
        "status": "active"
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          "description": "qualificationPeriod must be less than 1461 full calendar days long"
        }
      ]
    }

Зміна терміну дії відборів
---------------------------

Під час зменшення/подовження терміну дії відборів система перевіряє максимально допустиме значення, на яке можна збільшувати відбір, та що нова дата не менша поточної дати внесення змін

Якщо відбір вже активований, то змінювати qualificaionPeriod напряму вже заборонено:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "qualificationPeriod": {
          "endDate": "2025-02-01T00:00:00+02:00"
        },
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "qualificationPeriod",
          "description": "Rogue field"
        }
      ]
    }

Для активних відборів для зміни терміну дії буде окремий ендпоінт додаткових угод.
В системі використовується термінологія "змін" / "changes".

.. sourcecode::

    /api/2.5/frameworks/{framework_id}/changes

Цей ендпоінт буде приймати наступну структуру:

.. sourcecode::

    {
      "data": {
        "rationale": "Відсутність подальшої потреби в закупівлі з використанням рамкової угоди",
        "rationaleTypes": ["noDemandFramework",],
        "modifications": {
          "qualificationPeriod": {
            "startDate": "2025-03-07T00:00:00+02:00",
            "endDate": "2025-02-01T00:00:00+02:00"
          },
        },
      }
    }

Замовник обов'язково вказує в додатковій угоді:

* `modifications` - це структура, що відображає зміни в полях відбору, які буде внесено

* `rationaleTypes` - підставу (обґрунтування) змін (наприклад обґрунтування подовження/зменшення терміну дії відбору)

* `rationale` - опис обґрунтування змін

В об'єкті `modifications` обов'язково необхідно вказати новий період:

* `qualificationPeriod.endDate` - кінцеву дату періоду розгляду заявок


Підстави для зміни терміну дії відборів:

- відсутності подальшої потреби в закупівлі з використанням рамкової угоди

- якщо здійснення кваліфікаційного відбору кандидатів до рамкової угоди стало неможливим внаслідок дії непереборної сили

- інше


Система перевіряє, що термін дії подовжено не більше ніж на максимально допустиме значення за один раз від дати внесення змін та що  нова дата qualificationPeriod:endDate не повинна бути менша ніж= поточна дата + 30 кд:


.. sourcecode:: http

    POST /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2/changes?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "modifications": {
          "qualificationPeriod": {
            "endDate": "2025-02-01T00:00:00+02:00"
          },
        },
        "rationaleTypes": ["noDemandFramework",],
        "rationale": "Відсутність подальшої потреби в закупівлі з використанням рамкової угоди",
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          "description": "qualificationPeriod.endDate couldn't be less than 30 full days from now"
        }
      ]
    }


.. sourcecode:: http

    POST /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2/changes?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "modifications": {
          "qualificationPeriod": {
            "endDate": "2030-02-01T00:00:00+02:00"
          },
        },
        "rationaleTypes": ["noDemandFramework",],
        "rationale": "Відсутність подальшої потреби в закупівлі з використанням рамкової угоди",
      }
    }


    HTTP/1.0 422 Unprocessable Entity
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          "description": "qualificationPeriod.endDate couldn't be more than 1461 full days from now"
        }
      ]
    }

Правильний запит на зміну терміну дії відбору:

.. sourcecode:: http

    POST /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2/changes?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "modifications": {
          "qualificationPeriod": {
            "endDate": "2025-04-10T00:00:00+02:00"
          },
        },
        "rationaleTypes": ["noDemandFramework",],
        "rationale": "Відсутність подальшої потреби в закупівлі з використанням рамкової угоди",
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json

    {
      "data": {
        "modifications": {
          "qualificationPeriod": {
            "endDate": "2025-04-10T00:00:00+02:00"
          },
        },
        "rationaleTypes": ["noDemandFramework",],
        "rationale": "Відсутність подальшої потреби в закупівлі з використанням рамкової угоди",
        "date": "2025-03-07T10:50:00+02:00",
        "id": "0c883e4482795b2a00a3b5bdaa043749"
      }
    }

Після того, як була створена додаткова угода, необхідно накласти підпис на ці зміни:

.. sourcecode:: http

    POST /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2/changes/0c883e4482795b2a00a3b5bdaa043749/documents?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "title": "sign.p7s",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/8b13e31b59384667b1631b1e0323599c?Signature=nCW5EbReV2Kv5cJW%2Fk1jbZNSfFoBVZSfqxXIPggisqqtwhDxMfD%2BRmNddoOHeaunLV6du8Vsiv2YjlbDQhpoDQ%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "sign/p7s",
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json

    {
      "data": {
        "id": "8c94a85001964beaa8b7a98af8df8566",
        "datePublished": "2025-03-07T10:50:00+02:00",
        "title": "sign.p7s",
        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/8b13e31b59384667b1631b1e0323599c?Signature=nCW5EbReV2Kv5cJW%2Fk1jbZNSfFoBVZSfqxXIPggisqqtwhDxMfD%2BRmNddoOHeaunLV6du8Vsiv2YjlbDQhpoDQ%3D%3D&KeyID=a8968c46",
        "hash": "md5:00000000000000000000000000000000",
        "format": "sign/p7s",
        "dateModified": "2025-03-07T10:50:00+02:00",
        "language": "uk"
      }
    }


Тепер до об'єкта changes ще додані документи:

* `documents` - накладання ЕЦП на зміни

Подивимося тепер як виглядає відбір - в нього з'явився новий об'єкт `changes`, який відображає історію всіх змін терміну дії відборів:

.. sourcecode:: http

    GET /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "data": {
        "prettyID": "UA-F-2024-01-01-000001",
        "title": "Framework",
        "description": "Framework desc",
        "status": "active",
        "classification": {
          "description": "Mustard seeds",
          "scheme": "ДК021",
          "id": "03111600-8"
        },
        "additionalClassifications": [
          {
            "scheme": "ДК003",
            "id": "17.21.1",
            "description": "папір і картон гофровані, паперова й картонна тара"
          }
        ],
        "documents": [
          {
            "id": "8c94a85001964beaa8b7a98af8df8566",
            "datePublished": "2025-01-01T12:00:00+02:00",
            "hash": "md5:00000000000000000000000000000000",
            "title": "framework.doc",
            "format": "application/msword",
            "url": "http://public-docs-sandbox.prozorro.gov.ua/get/f5cb842886f141e681b47175faee1ea1?Signature=G7BvnAz3bGtcoEJQ4VMw2s9ARIPKFD0ZsNnTzvkGoYumAUv61r%2BTP0NXiTQhwebXxqUJM1d5aNg5AU8LtKBSCw%3D%3D&KeyID=a8968c46",
            "dateModified": "2025-01-01T12:00:00+02:00",
            "language": "uk"
          },
          {
            "id": "cbf1f425f5234b3584c2b0fd8b3f3232",
            "datePublished": "2025-01-01T12:00:00+02:00",
            "hash": "md5:00000000000000000000000000000000",
            "title": "framework_additional_docs.doc",
            "format": "application/msword",
            "url": "http://public-docs-sandbox.prozorro.gov.ua/get/beda32f664fb459291d362e650147d5d?Signature=pcYNBP%2FAj04nzgykslGVmqMOd3wtV9PptoB5NuzsDBne78GS2HGn9hmq%2ByTIhaYOr%2Bdtv6mO63IBY8NkQ3jrAg%3D%3D&KeyID=a8968c46",
            "dateModified": "2025-01-01T12:00:00+02:00",
            "language": "uk"
          },
          {
            "id": "cbf1f425f5234b3584c2b0fd8b3f3232",
            "datePublished": "2025-01-01T12:00:00+02:00",
            "hash": "md5:00000000000000000000000000000000",
            "title": "framework_additional_docs.doc",
            "format": "application/msword",
            "url": "http://public-docs-sandbox.prozorro.gov.ua/get/d369fa8572584fffba4fe7fb70daffe2?Signature=%2B8G4s2LtJtEl9ij7xF17ayvO5H1BxrBWc7bAMhNt6pn9JkPAOCocA1BAkf3wIPgRzu8bKDe4qvayMpJcnL%2FlAQ%3D%3D&KeyID=a8968c46",
            "dateModified": "2025-01-01T12:00:00+02:00",
            "language": "uk"
          }
        ],
        "owner": "broker",
        "date": "2025-01-02T12:00:00+02:00",
        "dateCreated": "2025-01-01T12:00:00+02:00",
        "dateModified": "2025-01-02T12:00:00+02:00",
        "qualificationPeriod": {
          "startDate": "2025-01-01T12:00:00+02:00",
          "endDate": "2025-04-10T00:00:00+02:00"
        },
        "frameworkType": "dynamicPurchasingSystem",
        "procuringEntity": {
          "name": "Державне управління справами",
          "identifier": {
            "scheme": "UA-EDR",
            "id": "00037256",
            "legalName": "Назва організації"
          },
          "address": {
            "countryName": "Україна",
            "streetAddress": "вул. Банкова, 11, корпус 1",
            "locality": "м. Київ",
            "region": "м. Київ",
            "postalCode": "01220"
          },
          "contactPoint": {
            "name": "Державне управління справами",
            "telephone": "+0440000001",
            "email": "aa@aa.com"
          },
          "kind": "general"
        },
        "enquiryPeriod": {
          "startDate": "2025-01-01T12:00:00+02:00",
          "endDate": "2025-01-16T12:00:00+02:00",
          "clarificationsUntil": "2025-01-19T00:00:00+02:00"
        },
        "period": {
          "startDate": "2025-01-01T12:00:00+02:00",
          "endDate": "2025-03-10T00:00:00+02:00"
        },
        "changes": [
          {
            "modifications": {
              "qualificationPeriod": {
                "endDate": "2025-04-10T00:00:00+02:00"
              },
            },
            "previous": {
              "qualificationPeriod": {
                "startDate": "2025-01-01T12:00:00+02:00",
                "endDate": "2027-02-01T00:00:00+02:00"
              },
            },
            "rationaleTypes": ["noDemandFramework",],
            "rationale": "Відсутність подальшої потреби в закупівлі з використанням рамкової угоди",
            "date": "2025-03-07T10:50:00+02:00",
            "id": "0c883e4482795b2a00a3b5bdaa043749",
            "documents": [
              {
                "id": "8c94a85001964beaa8b7a98af8df8566",
                "datePublished": "2025-03-07T10:50:00+02:00",
                "title": "sign.p7s",
                "url": "http://public-docs-sandbox.prozorro.gov.ua/get/8b13e31b59384667b1631b1e0323599c?Signature=nCW5EbReV2Kv5cJW%2Fk1jbZNSfFoBVZSfqxXIPggisqqtwhDxMfD%2BRmNddoOHeaunLV6du8Vsiv2YjlbDQhpoDQ%3D%3D&KeyID=a8968c46",
                "hash": "md5:00000000000000000000000000000000",
                "format": "sign/p7s",
                "dateModified": "2025-03-07T10:50:00+02:00",
                "language": "uk"
              }
            ]
          }
        ],
        "next_check": "2025-03-10T00:00:00+02:00",
        "id": "a00a3b5bdaa0437490c883e4482795b2"
      },
      "config": {
        "restrictedDerivatives": false,
        "clarificationUntilDuration": 3,
        "qualificationComplainDuration": 0,
        "hasItems": false
      }
    }

Варіант №1 додавання changes без статусів
------------------------------------------

Флоу зміни періода (так як описано вище):

1) створюємо `change` з новим `qualificationPeriod`
2) після створення одразу у відборі змінюється `qualificationPeriod`, а попередній записується в об'єкті `changes` в полі `previous`
3) підписується `change` вже з новим значенням `qualificationPeriod` у відборі (через context)


Варіант №2 додавання changes зі статусами
------------------------------------------

Флоу зміни періода:

1) створюємо `change` з новим `qualificationPeriod` (статус `pending`)
2) після створення у відборі поки що НЕ ЗМІНЮЄТЬСЯ `qualificationPeriod`, і НЕ ЗАПИСУЄТЬСЯ попередній період в об'єкті `changes` в полі `previous`
3) підписується відбір з ПОПЕРЕДНІМ значенням `qualificationPeriod`
4) `change` переводиться в статус `active` через PATCH
5) після активації `change` у відборі змінюється `qualificationPeriod`, а попередній записується в об'єкті `changes` в полі `previous`
6) також є можливість `pending` ченж перевести в статус `cancelled` за допомогою PATCH. Після цього не можна буде підписати або активувати ці зміни, а тільки додати нові, якщо необхідно.

Плюси цього підходу:

* маємо таку саму структуру `changes` зі статусами як і у контрактах, і в CFAUA agreements

Мінуси, над якими треба подумати:

* підписується фреймворк з поперднім значенням `qualificationPeriod`, бо ще не активували `change`


Валідації для закупівель
-------------------------

Список помилок пов’язаних з угодою, які можуть виникати при створенні тендеру:

* Agreement not found in agreements
* tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)
* Agreement with/without items is not allowed

Список помилок пов’язаних з угодою, які можуть виникати при активації тендеру:

* Agreement not found in agreements
* Agreement status is not active
* Agreement has less than 3 active contracts
* tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)
* Agreement with/without items is not allowed

При подачі пропозиції у вже оголошені тендери:

* Bid is not a member of agreement (should be active contract with the same supplier)
* Bid value.amount can't be greater than contact value.amount.
* Can't post inconsistent bid (check parameters values in contract and bid)


Зміна статусу `agreement.contracts`
------------------------------------

Зміна статусів агріменту, контракту та майлстоунів (як працює зараз):

1) Хронографом: коли закінчується `agreement.period.endDate`:

* `agreement` переходить в статус `terminated`
* `active` contracts переходять в статус `terminated`
* всі `scheduled` `contract.milestones` змінюють статус на:
    - met, якщо є dueDate і dueDate <= now
    - notMet, якщо немає dueDate або dueDate > now

2) Замовником вручну: при PATCH зміні статусу `contract.milestone` на `met`:

* `contract` переходить в статус `terminated`
* всі інші `scheduled` `contract.milestones` змінюють статус на `notMet`

3) Хронографом: коли закінчується `dueDate` у `scheduled` `milestone["type"] == "ban"` але ще не закінчується `agreement.period.endDate`:

* `suspended` `contracts` переходять в статус `active`, `milestone → met`

4) Замовником вручну: при POST `milestone` з типом `ban`

* `contract` переходить в статус `suspended`

.. note::

    Буде змінено пункт 1 і 2.

Зміна статусів агріменту та майлстоунів, яка очікується:

1) Хронографом: коли закінчується `agreement.period.endDate`:

* `agreement` переходить в статус `terminated`
* всі `scheduled` `contract.milestones` змінюють статус на:
    - met, якщо є dueDate і dueDate <= now
    - notMet, якщо немає dueDate або dueDate > now

2) Замовником вручну: при PATCH зміні статусу `contract.milestone` на `met`:

* всі інші `scheduled` `contract.milestones` змінюють статус на `notMet`

Зміну статусу контракту залишиться тільки при умові пункту 3 і 4 (тобто при додаванні бану і закінченню терміна бану).