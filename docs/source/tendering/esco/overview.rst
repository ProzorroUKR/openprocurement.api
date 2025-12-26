Огляд
=====

The Open Procurement `ESCO` procedure is plugin to `Open Procurement API` software.

REST-ful інтерфейс для плагіна відповідає основним принципам дизайну програмного забезпечення. 


Домовленості
------------

Цей плагін підтримує `домовленості Open Procurement API <http://api-docs.openprocurement.org/en/latest/overview.html#conventions>`_.

Основні задачі
--------------

ESCO procedure is applied for all energy service procurements regardless their price. The main assessment criterion for this type of procurement procedure is Net Present Value (NPV). ESCO procedure features reverse approach compared to the other openprocurement procedures: tender is won by supplier who offered the highest Net Present Value. 

The `procurementMethodType` is `esco`.

ESCO contracts use separate extension: https://github.com/openprocurement/openprocurement.contract.esco


Стан проекту
------------

Цей проект активно розробляється і має пілотні встановлення.

Репозиторій цього проекту є на GitHub: https://github.com/openprocurement/openprocurement.tender.esco

Повідомляйте про всі проблеми та поради через `issue tracker <https://github.com/openprocurement/openprocurement.tender.esco/issues>`_ (реєстрація на GitHub обов’язкова). Загальне обговорення відбувається через розсилку `Open Procurement General <https://groups.google.com/group/open-procurement-general>`_.

API stability
-------------
API is highly unstable, and while API endpoints are expected to remain relatively stable the data exchange formats are expected to be changed a lot.  The changes in the API are communicated via `Open Procurement API maillist <https://groups.google.com/group/open-procurement-api>`_.
