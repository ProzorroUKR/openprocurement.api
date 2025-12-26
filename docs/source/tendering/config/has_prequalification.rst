.. _has_prequalification:

hasPrequalification
===================

Field `hasPrequalification` is a boolean field that indicates whether the tender has an pre qualification stage or not.

Possible values for `hasPrequalification` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-prequalification-values.csv
   :header-rows: 1

hasPrequalification is `true`
-----------------------------

Приклад використання:

* :ref:`openeu` → :ref:`openeu_tutorial`
* :ref:`esco` → :ref:`esco_tutorial`
* :ref:`competitivedialogue` → :ref:`competitivedialogue_tutorial`
* :ref:`cfaua` → :ref:`cfaua_tutorial`

hasPrequalification is `false`
------------------------------

Приклад використання:

* :ref:`belowthreshold` → :ref:`tutorial`
* :ref:`open` → :ref:`open_tutorial`
* :ref:`openua` → :ref:`openua_tutorial`
* :ref:`defense` → :ref:`defense_tutorial`
* :ref:`limited` → :ref:`limited_tutorial`
* :ref:`cfaselectionua` → :ref:`cfaselection_tutorial`
* :ref:`pricequotation` → :ref:`pricequotation_tutorial`
