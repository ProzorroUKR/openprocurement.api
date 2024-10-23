.. _dps_long_short:

DPS Long VS Short
=================

Відбір
------
У відборі (1 етап) замовник самостійно зазначає
чи він буде деталізувати предмети закупівлі на першому етапі,
чи він це зробить безпосереньо в закупівлі.

Замовник на етапі створення відбору може вибрати, чи буде він деталізувати предмети закупівлі на першому етапі, за допомогою встановлення конфігурації процедури `hasItems`

.. sourcecode::

    hasItems = true | false

Висока деталізація відбору визначає,
що всі питання/скраги до предмету закупівлі будуть вирішені на етпапі відбору.
закупівля буде, відповідно, - коротка.

Framework з деталізацією
------------------------

Створюємо відбір з деталізацією:

.. sourcecode:: http

    POST /api/2.5/frameworks HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "config": {
        "hasItems": true,
        ...
      },
      "data": {
        "frameworkType": "dynamicPurchasingSystem",
         ...
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/frameworks/4178f66eebf04c4497d0fb223feeb0fe

    {
      "config": {
        "hasItems": true,
        ...
      },
      "data": {
        "status": "draft",
        "frameworkType": "dynamicPurchasingSystem",
        ...
    }


Якщо спробувати активувати відбір з `hasItems: true`, і не вказати `items`, отримаємо помилку:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/4178f66eebf04c4497d0fb223feeb0fe?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "status": "active"
      }
    }

    HTTP/1.0 400 Bad Request
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          ...
        }
      ]
    }


Додавання `items` у відбір відбувається через PATCH запит:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/4178f66eebf04c4497d0fb223feeb0fe?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "items": [
          ...
        ]
      }
    }

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "config": {
        "hasItems": true,
        ...
      },
      "data": {
        "frameworkType": "dynamicPurchasingSystem",
        "status": "draft",
        "items": [
            ...
        ],
        ...
      }
    }

Тепер активуємо відбір:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/4178f66eebf04c4497d0fb223feeb0fe?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
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
      "config": {
        "hasItems": true,
        ...
      },
      "data": {
        "frameworkType": "dynamicPurchasingSystem",
        "status": "active",
        "items": [
            ...
        ],
        ...
      }
    }


Відбір без деталізації
----------------------

Створюємо відбір без деталізації:

.. sourcecode:: http

    POST /api/2.5/frameworks HTTP/1.0
    Authorization: Bearer broker
    Content-Length: 1874
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "config": {
        "hasItems": false,
        ...
      },
      "data": {
        "frameworkType": "dynamicPurchasingSystem",
        ...
      }
    }


    HTTP/1.0 201 Created
    Content-Type: application/json
    Location: http://lb-api-sandbox.prozorro.gov.ua/api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2

    {
      "config": {
        "hasItems": false,
        ...
      },
      "data": {
        "status": "draft",
        "frameworkType": "dynamicPurchasingSystem",
        ...
    }

Спробуємо додати `items` у відбір:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "items": [
          ...
        ]
      }
    }

    HTTP/1.0 400 Bad Request
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          ...
        }
      ]
    }

Отримаємо помилку, що `items` не можуть бути додані до відбору без деталізації.

Активуємо відбір:

.. sourcecode:: http

    PATCH /api/2.5/frameworks/a00a3b5bdaa0437490c883e4482795b2?acc_token=2a5f07868aed43bfb10588a5ac40185a HTTP/1.0
    Authorization: Bearer broker
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
      "config": {
        "hasItems": true,
        ...
      },
      "data": {
        "frameworkType": "dynamicPurchasingSystem",
        "status": "active",
        ...
      }
    }

Угода
=====

Результатом відбору є угода.

Конфігурація деталізації предмету закупівлі в угоді відповідає конфігурації відбору. Власне деталізація предмету у вигляді поля `items` в угоді відповідає `items` відбору.

.. sourcecode::

  GET /api/2.5/agreements/4178f66eebf04c4497d0fb223feeb0fe HTTP/1.0

  HTTP/1.0 200 OK
  Content-Type: application/json

  {
    "config": {
      "hasItems": true,
      ...
    },
    "data": {
      "items": [
        ...
      ]
    }
  }

Tender
======

Другий етап у вигляді закупівлі посилається на угоду. 

Якщо угода має деталізацію предмету закупівлі ("hasItems": true),
то закупівля буде скороченою без оскарження.

.. sourcecode:: http


    POST /api/2.5/tenders  HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "procurementMethodType": "competitiveOrdering",
        "agreements": [
          {
            "id": "4178f66eebf04c4497d0fb223feeb0fe"
          }
        ],
        ...
      },
      "config": {
         "tenderPeriodMinDays": 3,
         "tenderComplaints": false,
         "tenderClaims": false,
         "awardComplaints": false,
         "awardClaims": false,
         "cancellationComplaints": false,
         ...
      }
    }


Якщо ж угода не має деталізації предмету закупівлі ("hasItems": false),
то закупівля буде довгою.

.. sourcecode:: http


    POST /api/2.5/tenders  HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "procurementMethodType": "competitiveOrdering",
        "agreements": [
          {
            "id": "4178f66eebf04c4497d0fb223feeb0fe"
          }
        ],
        ...
      },
      "config": {
         "tenderPeriodMinDays": 7,
         "tenderComplaints": true,
         "tenderClaims": true,
         "awardComplaints": true,
         "awardClaims": true,
         "cancellationComplaints": true,
         ...
      }
    }

Вищевказані конфіги мають різні значення відповідно до деталізації відбору/угоди.
І можуть бути винесені в окоремі файли в стандартах.

Отут можна ознайомитись з запропонованими змінами до стандартів
https://github.com/ProzorroUKR/standards/pull/203/files

Тут видно, що для процедури competitiveOrdering.json
вцілому є два значення

.. sourcecode::

    "tenderPeriodMinDays": {
      "type": "integer",
      "enum": [
        7,
        3
      ],
      "default": 7
    },

то в окремому фалйлі для довгої процедури
'competitiveOrdering.long.json' буде одне

.. sourcecode::

    "tenderPeriodMinDays": {
      "type": "integer",
      "enum": [
        7
      ],
      "default": 7
    },

Але це все ще один "procurementMethodType: competitiveOrdering"

DPS Short
---------

Cкорочена процедура - тендер, який не містить оскарження у вигляді подання скарг до АМКУ на будь якому етапі, де таке оскарження виникає.

Використанні наступні конфіги - параметри, що визначають наявність або відсутність у закупівлі оскарження в тендері:

* hasTenderComplaints - оскарження умов ТД

* hasAwardComplaints - оскарження рішення по кваліфікації

* hasCancellationComplaints - оскарження скасування тендеру

Запитання/вимоги як функціонал лишаються та відбувається за процесом, притаманним ВТО.

Для скороченої процедури без оскарження ці параметри будуть мати одне тільки значення `False`:

.. sourcecode:: http


    POST /api/2.5/tenders  HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        "procurementMethodType": "competitiveOrdering",
        "agreements": [
          {
            "id": "4178f66eebf04c4497d0fb223feeb0fe"
          }
        ],
        ...
      },
      "config": {
         "hasTenderComplaints": false,
         "hasAwardComplaints": false,
         "hasCancellationComplaints": false,
         ...
      }
    }


При створенні закупівлі не буде додаватися `complaintPeriod` автоматично, як це працює зараз в відкритих торгах з особливостями. І тому при спробі подати скаргу на умови ТД користувач буде отримувати помилку:


.. sourcecode:: http


    POST /api/2.5/tenders/1218f66eebf04c4497d0fb223feeb121/complaints HTTP/1.0
    Authorization: Bearer broker
    Content-Type: application/json
    Host: lb-api-sandbox.prozorro.gov.ua

    {
      "data": {
        ...
      }
    }

    HTTP/1.0 403 Forbidden
    Content-Type: application/json

    {
      "status": "error",
      "errors": [
        {
          "location": "body",
          "name": "data",
          "description": "Can't add complaint as it is forbidden by configuration"
        }
      ]
    }

Схожі помилки будуть при поданні скарги на рішення по кваліфікації та скарги на скасування тендеру.