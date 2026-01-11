.. _opt_fields:

Опціональні поля (opt_fields)
==============================

Параметр ``opt_fields`` дозволяє додати додаткові поля до відповіді API. Це дозволяє отримувати тільки необхідні дані, зменшуючи обсяг переданої інформації та прискорюючи обробку.

Використання
------------

Параметр ``opt_fields`` вказується як URL параметр зі списком полів, розділених комою:

.. code-block:: http

   GET /api/0/tenders?opt_fields=status,dateCreated,public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Загальні поля
-------------

Наступні поля доступні для всіх типів feed ендпоінтів:

- ``public_modified``

Тендери (Tenders)
------------------

Feed
~~~~

Для feed ендпоінта ``/api/0/tenders`` доступні наступні поля:

- ``dateCreated``
- ``dateModified``
- ``tenderPeriod``
- ``qualificationPeriod``
- ``auctionPeriod``
- ``awardPeriod``
- ``status``
- ``tenderID``
- ``lots``
- ``contracts``
- ``agreements``
- ``procuringEntity``
- ``procurementMethodType``
- ``procurementMethod``
- ``next_check``
- ``mode``
- ``stage2TenderID``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/tenders?opt_fields=status,dateCreated,procuringEntity HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/tenders/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/tenders/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Контракти (Contracts)
---------------------

Feed
~~~~

Для feed ендпоінта ``/api/0/contracts`` доступні наступні поля:

- ``dateCreated``
- ``contractID``
- ``dateModified``
- ``status``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/contracts?opt_fields=status,contractID,dateCreated HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/contracts/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/contracts/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Плани (Plans)
-------------

Feed
~~~~

Для feed ендпоінта ``/api/0/plans`` доступні наступні поля:

- ``dateCreated``
- ``dateModified``
- ``status``
- ``planID``
- ``procuringEntity``
- ``procurementMethodType``
- ``mode``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/plans?opt_fields=status,planID,procuringEntity HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/plans/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/plans/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Фреймворки (Frameworks)
-----------------------

Feed
~~~~

Для feed ендпоінта ``/api/0/frameworks`` доступні наступні поля:

- ``dateCreated``
- ``dateModified``
- ``id``
- ``title``
- ``prettyID``
- ``enquiryPeriod``
- ``period``
- ``qualificationPeriod``
- ``status``
- ``frameworkType``
- ``next_check``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/frameworks?opt_fields=status,title,frameworkType HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/frameworks/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/frameworks/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Подання (Submissions)
---------------------

Feed
~~~~

Для feed ендпоінта ``/api/0/submissions`` доступні наступні поля:

- ``dateCreated``
- ``dateModified``
- ``id``
- ``frameworkID``
- ``qualificationID``
- ``submissionType``
- ``status``
- ``tenderers``
- ``documents``
- ``date``
- ``datePublished``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/submissions?opt_fields=status,submissionType,frameworkID HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/submissions/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/submissions/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Кваліфікації (Qualifications)
------------------------------

Feed
~~~~

Для feed ендпоінта ``/api/0/qualifications`` доступні наступні поля:

- ``dateModified``
- ``dateCreated``
- ``id``
- ``frameworkID``
- ``submissionID``
- ``qualificationType``
- ``status``
- ``documents``
- ``date``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/qualifications?opt_fields=status,qualificationType,frameworkID HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/qualifications/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/qualifications/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua

Угоди (Agreements)
------------------

Feed
~~~~

Для feed ендпоінта ``/api/0/agreements`` доступні наступні поля:

- ``dateCreated``
- ``dateModified``
- ``id``
- ``agreementID``
- ``agreementType``
- ``status``
- ``tender_id``
- ``next_check``
- ``procuringEntity``
- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/agreements?opt_fields=status,agreementID,agreementType HTTP/1.1
   Host: public-api.prozorro.gov.ua

Детальний
~~~~~~~~~

Для детального ендпоінта ``/api/0/agreements/{id}`` доступне наступне поле:

- ``public_modified``

Приклад:

.. code-block:: http

   GET /api/0/agreements/{id}?opt_fields=public_modified HTTP/1.1
   Host: public-api.prozorro.gov.ua
