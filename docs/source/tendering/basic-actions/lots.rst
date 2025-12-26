.. _lots:

Багатолотові закупівлі
======================

Якщо є закупівля з декількома різними елементами, що можуть бути куплені у різних постачальників, то можна розділити цю процедуру закупівлі на :ref:`лоти <lot>`. Кожен лот має свій власний бюджет (`Lot.value`).

Більш детальну інформацію шукайте на сторінці `Багатолотові закупівлі <http://openprocurement.org/ua/multilots.html>`_.

.. sourcecode:: json

  {
    "lots": [
      {
        "id": "7d774fbf1e86420484c7d1a005cc283f",
        "title": "Lot #1: Kyiv stationey",
        "description": "Items for Kyiv office",
        "value": {"currency": "UAH", "amount": 8000.0, "valueAddedTaxIncluded": true},
        "minimalStep": {"currency": "UAH", "amount": 30.0, "valueAddedTaxIncluded": true},
        "status": "active"
      }, {
        "id": "563ef5d999f34d36a5a0e4e4d91d7be1",
        "title": "Lot #1: Lviv stationey",
        "description": "Items for Lviv office",
        "value": {"currency": "UAH", "amount": 9000.0, "valueAddedTaxIncluded": true},
        "minimalStep": {"currency": "UAH", "amount": 35.0, "valueAddedTaxIncluded": true},
        "status": "active"
      }
    ]
  }

Багатолотова закупівля може мати документацію для процедури в цілому, окремо для лота та окремо для елемента.

.. sourcecode:: json

  {
    "documents": [
      {
        "format": "application/msword",
        "url": "...",
        "title": "kyiv-specs.doc",
        "datePublished": "2015-10-27T14:01:16.155803+02:00",
        "dateModified": "2015-10-27T14:01:16.155844+02:00",
        "id": "9491647572294c2bb20bf28f16d14dd8",
        "documentOf": "lot",
        "relateLot": "7d774fbf1e86420484c7d1a005cc283f"
      }
    ]
  }

Те саме стосується і :ref:`звернень <question>` та відповідей. Звернення може бути по процедурі в цілому, окремо для лота та окремо для елемента.

На торгах учасник може подавати пропозицію для одного лота, декількох лотів, або навіть для всіх лотів закупівлі.

.. sourcecode:: json

  {
    "lotValues": [
      {
        "value": {"currency": "UAH", "amount": 7750.0, "valueAddedTaxIncluded": true},
        "reatedLot": "7d774fbf1e86420484c7d1a005cc283f",
        "date": "2015-11-01T12:43:12.482645+02:00"
      }, {
        "value": {"currency": "UAH", "amount": 8125.0, "valueAddedTaxIncluded": true},
        "reatedLot": "563ef5d999f34d36a5a0e4e4d91d7be1",
        "date": "2015-11-01T12:43:12.482645+02:00"
      }
    ],
    "..."
  }

Кожен :ref:`документ <document>`, вкладений до :ref:`пропозиції <bid>`, може стосуватись процедури в цілому, окремого лота або окремого елемента.

Кожен лот має окремий аукціон та процес визначення переможця.

Кожен лот можна скасувати окремо, не впливаючи на інші лоти.

Оголошення багатолотової закупівлі
----------------------------------

Багатолотова закупівля створюється в декілька кроків. Спочатку потрібно створити закупівлю з декількома елементами.

.. sourcecode:: http

  POST /tenders HTTP/1.1

  {"data": {
     "items":[
        {"description": "", ... },
        {"description": "", ... }
       ],
     ...
    }}

.. sourcecode:: http

  HTTP/1.1 201 Created
  Location: /tenders/64e93250be76435397e8c992ed4214d1

  {"data": {
    "items":[
        {"id": "c25264295db0463ba533fd380756cff1", "description": "", ... },
        {"id": "f94aa51e2af944e08e02a4063121f93c", "description": "", ... }
      ],
    ...
    },
    ...
  }

Потім потрібно додати всі лоти окремими запитами.

.. sourcecode:: http

  POST /tenders/64e93250be76435397e8c992ed4214d1/lots HTTP/1.1

  {"data": {..}}

.. sourcecode:: http

  HTTP/1.1 201 Created
  Location: /tenders/64e93250be76435397e8c992ed4214d1/lots/7d774fbf1e86420484c7d1a005cc283f

Другий лот:

.. sourcecode:: http

  POST /tenders/64e93250be76435397e8c992ed4214d1/lots HTTP/1.1

  {"data": {..}}

.. sourcecode:: http

  HTTP/1.1 201 Created
  Location: /tenders/64e93250be76435397e8c992ed4214d1/lots/563ef5d999f34d36a5a0e4e4d91d7be1

Елементи повинні бути розподілені по лотах.

.. sourcecode:: http

  PATCH /tenders/64e93250be76435397e8c992ed4214d1 HTTP/1.1

  {"data": {
    "items":[
        {"id": "c25264295db0463ba533fd380756cff1", "relatedLot": "7d774fbf1e86420484c7d1a005cc283f"},
        {"id": "f94aa51e2af944e08e02a4063121f93c", "relatedLot": "563ef5d999f34d36a5a0e4e4d91d7be1"}
      ],
    ...
    },
    ...
  }

Подання пропозицій у багатолотовій закупівлі
--------------------------------------------

Цінова пропозиція повинна мати властивість `lotValues`, що складається з декількох об’єктів :ref:`LotValue`. Кожен з них повинен посилатись на лот, до якого подана пропозиція, через властивість `relatedLot`.

.. sourcecode:: http

  POST /tenders/64e93250be76435397e8c992ed4214d1/bids HTTP/1.1

  {"data": {
    "lotValues": [
      {
        "value": {"currency": "UAH", "amount": 7750.0, "valueAddedTaxIncluded": true},
        "reatedLot": "7d774fbf1e86420484c7d1a005cc283f",
        "date": "2015-11-01T12:43:12.482645+02:00"
      }, {
        "value": {"currency": "UAH", "amount": 8125.0, "valueAddedTaxIncluded": true},
        "reatedLot": "563ef5d999f34d36a5a0e4e4d91d7be1",
        "date": "2015-11-01T12:43:12.482645+02:00"
      }
    ],
    ...
  }}

.. sourcecode:: http

  HTTP/1.1 201 Created
  Location: /tenders/64e93250be76435397e8c992ed4214d1/bids/ae836da01ef749e494427dc591d36062

URL-адреси для участі в аукціоні будуть доступні для кожного з поданих лотів.

Кваліфікація у багатолотових закупівлях
---------------------------------------

ПІсля завершення аукціонів для кожного лота розпочинається його власний процес визначення переможця. Тобто, у :ref:`Tender` створюється декілька об’єктів визначення переможця і кожен з них вимагає рішення (дискваліфікації чи прийняття).

.. sourcecode:: http

  GET /tenders/64e93250be76435397e8c992ed4214d1/awards HTTP/1.1

.. sourcecode:: http

  HTTP/1.1 200 OK

  {"data": [
      {
          "status": "pending",
          "bid_id": "ae836da01ef749e494427dc591d36062",
          "value": {"currency": "UAH", "amount": 7750.0, "valueAddedTaxIncluded": true},
          "id": "c3179dd8609340a7ba9e5fe91762f564",
          "lotId": "7d774fbf1e86420484c7d1a005cc283f",
          "..."
      }, {
          "status": "pending",
          "bid_id": "ae836da01ef749e494427dc591d36062",
          "value": {"currency": "UAH", "amount": 8125.0, "valueAddedTaxIncluded": true},
          "id": "c99e30174b10418bac026a77d41288d7",
          "lotId": "563ef5d999f34d36a5a0e4e4d91d7be1",
          "..."
      }
    ]
  }


Після того, як завершуються всі кваліфікаційні процеси та всі періоди зупинок, вся закупівля змінює статус або на "завершена", або на "не відбулась" (якщо визначення переможців для всіх лотів `не відбулись`).

