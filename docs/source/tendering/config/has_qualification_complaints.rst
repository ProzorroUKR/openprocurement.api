.. _has_qualification_complaints:

hasQualificationComplaints
==========================

Поле `hasQualificationComplaints` - логічне поле, яке визначає наявність або відсутність оскарження закупівлі (звернення до АМКУ у вигляді скарги) після попереднього кваліфікаційного відбору учасників.

Можливі значення для поля `hasQualificationComplaints` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/has-qualification-complaints-values.csv
   :header-rows: 1

hasQualificationComplaints is `true`
------------------------------------

Приклад використання:

* :ref:`openeu` → :ref:`openeu_tutorial`
* :ref:`esco` → :ref:`esco_tutorial`
* :ref:`competitivedialogue` → :ref:`competitivedialogue_tutorial`
* :ref:`cfaua` → :ref:`cfaua_tutorial`

hasQualificationComplaints is `false`
-------------------------------------

Приклад використання:

* :ref:`belowthreshold` → :ref:`tutorial`
* :ref:`open` → :ref:`open_tutorial`
* :ref:`openua` → :ref:`openua_tutorial`
* :ref:`defense` → :ref:`defense_tutorial`
* :ref:`limited` → :ref:`limited_tutorial`
* :ref:`cfaselectionua` → :ref:`cfaselection_tutorial`
* :ref:`pricequotation` → :ref:`pricequotation_tutorial`
