.. _cancellation_complaints:

hasCancellationComplaints
=========================

Поле `hasCancellationComplaints` є булевим полем, яке визначає наявність або відсутність у закупівлі оскарження (звернення до АМКУ за допомогою скарги) після скасування процедури.

Можливі значення для поля `hasCancellationComplaints` залежать від поля `procurementMethodType`.

.. csv-table::
   :file: csv/hasCancellationComplaints-values.csv
   :header-rows: 1

hasCancellationComplaints is `false`
------------------------------------

Приклад використання:
    * :ref:`competitiveordering` → :ref:`competitiveordering_short_tutorial`


hasCancellationComplaints is `true`
-----------------------------------

Приклад використання:
    * :ref:`open` → :ref:`open_tutorial`
