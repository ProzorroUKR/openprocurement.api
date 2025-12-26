.. _award_complaints:

hasAwardComplaints
==================

Поле `hasAwardComplaints` є булевим полем, яке визначає наявність або відсутність у закупівлі оскарження (звернення до АМКУ за допомогою скарги) рішення по кваліфікації учасників.

Можливі значення для поля `hasAwardComplaints` залежать від поля `procurementMethodType`.

.. csv-table::
   :file: csv/hasAwardComplaints-values.csv
   :header-rows: 1

hasAwardComplaints is `false`
-----------------------------

Приклад використання:
    * :ref:`competitiveordering` → :ref:`competitiveordering_short_tutorial`


hasAwardComplaints is `true`
----------------------------

Приклад використання:
    * :ref:`open` → :ref:`open_tutorial`
