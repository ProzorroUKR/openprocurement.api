.. _awarding_prolongation:

Awarding prolongation (DRAFT)
=============================

Опис задачі
-----------

Коли в процедурі сформувався award, треба зафіксувати що він створений і є 5 робочих днів на його оцінку та прийняття (status: active або status: unsuccessful). У разі неможливості прийняти рішення за робочих 5 днів замовник може продовжити розгляд до 20 робочих днів шляхом додавання причини продовження (description) та накладання підпису таким чином щоб система змогла сформувати з нього пдф е-протоколу продовження строку авард.

Дані що потрібно зафіксувати в апі
----------------------------------

Користувацький інпут:

- обгрунтування продовження строків розгляду: текстове поле
- файл підпису продовження строків розгляду: документ

Автоматична генерація:

- дата початку розгляду: дата, дата створення аварду

- дата кінця розгляду: дата, розраховується як:

  - дата початку розгляду + 5 робочих днів, якщо не було продовження
  - дата початку розгляду + 20 робочих днів, якщо було продовження

- дата продовження строків розгляду: дата, дата створення продовження

Пропозиція щодо реалізації: Період розгляду + майлстоун
-------------------------------------------------------

Об'єкт `period` що створюється разом зі створенням аварду і змінює дату dueDate при подовенні строків розгляду.

продовження строків розгляду відбувається за допомогою створення майлстоуна `prolongation`.

Крок 1
~~~~~~

Разом зі створенням аварду створюється об'єкт `period` з датами початку та кінця розгляду

Подивись як виглядає авард одразу після створення:

.. sourcecode:: http

  GET /api/2.5/tenders/acc230d5bfa642958a52d3389b38f7b4/awards/62810a506e7f43a4831dd68565b516ce HTTP/1.0

  Authorization: Bearer broker
  Content-Length: 2918
  Content-Type: application/json
  Host: lb-api-sandbox.prozorro.gov.ua

  HTTP/1.0 200 OK
  Content-Type: application/json

  {
    "id": "62810a506e7f43a4831dd68565b516ce",
    "status": "pending",
    "date": "2024-01-01T17:30:00.000000+02:00",
    "value": {...},
    "suppliers": [...],
    "bid_id": "4372bcd7b73b46998819584efe12505d",
    "lotID": "ee93ee67af68971ad033a41fb4e3551d",
    "documents": [...],
    "qualified": true,
    "eligible": true,
    "complaintPeriod": {...},
    "period": {
      "startDate": "2024-01-01T18:39:21.579086+02:00",
      "endDate": "2024-01-26T18:39:21.579086+02:00",
    },
  }

де:

- дата початку розгляду:

.. code-block::

    period.startDate

- дата кінця розгляду (дата початку розгляду + 5 робочих днів):

.. code-block::

    period.dueDate

Крок 2
~~~~~~

продовжимо розгляд шляхом додавання майлстоуна `prolongation`:

.. sourcecode:: http

  POST /api/2.5/tenders/acc230d5bfa642958a52d3389b38f7b4/awards/62810a506e7f43a4831dd68565b516ce/milestones HTTP/1.0

  Authorization: Bearer broker
  Content-Length: 2918
  Content-Type: application/json
  Host: lb-api-sandbox.prozorro.gov.ua

  {
    "code": "prolongation",
    "description": "Обгрунтування продовження строків розгляду",
  }

  HTTP/1.0 200 OK
  Content-Type: application/json

  {
    "id": "ba7457aa4a66410e8873e3129658d62d",
    "date": "2024-01-01T17:30:00.000000+02:00",
    "code": "prolongation",
    "dueDate": "2024-01-26T18:39:21.579086+02:00",
    "description": "Обгрунтування продовження строків розгляду",
  }

де:

- обгрунтування продовження строків розгляду:

.. code-block::

    description

- дата продовження строків розгляду:

.. code-block::

    date

- дата кінця розгляду (дата початку розгляду + 20 робочих днів):

.. code-block::

    dueDate

в award система автоматично встановлює новий `period.endDate` як `period.startDate` + 20 робочих днів

Крок 3
~~~~~~

Додаємо документ підпису на продовження:

.. sourcecode:: http

  POST /api/2.5/tenders/acc230d5bfa642958a52d3389b38f7b4/awards/62810a506e7f43a4831dd68565b516ce/documents HTTP/1.0

  Authorization: Bearer broker
  Content-Length: 2918
  Content-Type: application/json
  Host: lb-api-sandbox.prozorro.gov.ua

  {
    "id": "f8e45a6ace18463792412fa5e01190c1",
    "title": "sign.p7s",
    "documentType": "prolongationForm",
    "url": "http://link_to_file"
  }

  HTTP/1.0 200 OK
  Content-Type: application/json

  {
    "id": "f8e45a6ace18463792412fa5e01190c1",
    "title": "sign.p7s",
    "documentType": "prolongationForm",
    "datePublished": "2024-01-04T17:30:00.000000+02:00",
    "url": "http://link_to_file"
  }

Крок 4
~~~~~~

Подивимось як виглядає авард після продовження строків розгляду:

.. sourcecode:: http

  GET /api/2.5/tenders/acc230d5bfa642958a52d3389b38f7b4/awards/62810a506e7f43a4831dd68565b516ce HTTP/1.0

  Authorization: Bearer broker
  Content-Length: 2918
  Content-Type: application/json
  Host: lb-api-sandbox.prozorro.gov.ua

  HTTP/1.0 200 OK
  Content-Type: application/json

  {
    "id": "62810a506e7f43a4831dd68565b516ce",
    "status": "pending",
    "date": "2024-01-01T17:30:00.000000+02:00",
    "value": {...},
    "suppliers": [...],
    "bid_id": "4372bcd7b73b46998819584efe12505d",
    "lotID": "ee93ee67af68971ad033a41fb4e3551d",
    "documents": [
      {
        "id": "f8e45a6ace18463792412fa5e01190c1",
        "title": "sign.p7s",
        "documentType": "prolongationForm",
        "datePublished": "2024-01-04T17:30:00.000000+02:00",
        "url": "http://link_to_file"
      }
    ]
    "qualified": true,
    "eligible": true,
    "complaintPeriod": {...},
    "period": {
      "startDate": "2024-01-01T18:39:21.579086+02:00",
      "endDate": "2024-01-26T18:39:21.579086+02:00",
    },
    "milestones": [
      {
        "id": "ba7457aa4a66410e8873e3129658d62d",
        "date": "2024-01-04T17:30:00.000000+02:00",
        "code": "prolongation",
        "dueDate": "2024-01-26T18:39:21.579086+02:00",
        "description": "Обгрунтування продовження строків розгляду",
      }
    ]
  }

де:

- дата початку розгляду:

.. code-block::

    period.startDate

- дата кінця розгляду (дата початку розгляду + 20 робочих днів):

.. code-block::

    period.endDate

.. code-block::

    milestones[?(@.code=='prolongation')].dueDate

- обгрунтування продовження строків розгляду:

.. code-block::

    milestones[?(@.code=='prolongation')].description

- дата продовження строків розгляду:

.. code-block::

    milestones[?(@.code=='prolongation')].date

.. warning::

    ↓ непряма ознака

.. code-block::

    documents[?(@.documentType=='prolongationForm')].datePublished

- файл підпису продовження строків розгляду:

.. code-block::

    documents[?(@.documentType=='prolongationForm')]
