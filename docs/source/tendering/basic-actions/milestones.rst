.. _milestones:

Етапи (Умови) оплати
====================

Інформація про оплату може бути зазначена за допомогою поля `milestones` що містить об’єкти :ref:`Milestone <milestone>`

.. http:example:: http/milestones/tender-post-milestones.http
   :code:


Давайте оновимо `milestones`:


.. http:example:: http/milestones/tender-patch-milestones.http
   :code:

Для мультилотових тендерів кожен об’єкт :ref:`Milestone <milestone>` може відноситись до конретного лоту


.. http:example:: http/milestones/tender-patch-lot-milestones.http
   :code:

Будте обачні, об’єкт :ref:`lot <lot>` не може бути видалено, якщо в нього вказані етапи оплати

.. http:example:: http/milestones/tender-delete-lot-milestones-error.http
   :code:

Поле `sequenceNumber` має бути послідовним від 1 до n, без пропусків і дублів для кожного лоту окремо або загалом для тендеру. Якщо вказано неправильне значення, то буде помилка:

.. http:example:: http/milestones/tender-patch-lot-milestones-invalid-sequence.http
   :code:

Всі майлстоуни в закупівлі повинні мати однакову логіку, вони всі мають посилатися на лот або всі мають посилатися на тендер. Якщо майлстоуни мають різну логіку посилання, то буде помилка:

.. http:example:: http/milestones/tender-patch-lot-milestones-invalid-relation.http
   :code:
