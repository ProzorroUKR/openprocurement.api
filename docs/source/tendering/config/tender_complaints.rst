.. _tender_complaints:

hasTenderComplaints
===================

Поле `hasTenderComplaints` є булевим полем, яке визначає наявність або відсутність у закупівлі оскарження (звернення до АМКУ за допомогою скарги) умов тендерної документації.

Можливі значення для поля `hasTenderComplaints` залежать від поля `procurementMethodType`.

.. csv-table::
   :file: csv/hasTenderComplaints-values.csv
   :header-rows: 1

hasTenderComplaints is `false`
------------------------------

Приклад використання:
    * :ref:`competitiveordering` → :ref:`competitiveordering_short_tutorial`


hasTenderComplaints is `true`
-----------------------------

Приклад використання:
    * :ref:`open` → :ref:`open_tutorial`
