.. _has_qualification_complaints:

hasQualificationComplaints
==========================

Field `hasQualificationComplaints` is a boolean field that determines the presence or absence of an appeal in the procurement (appeal to the AMCU by means of a complaint) after preliminary prequalification of participants.

Possible values for `hasQualificationComplaints` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-qualification-complaints-values.csv
   :header-rows: 1

hasQualificationComplaints is `true`
------------------------------------

Example tutorials:

* :ref:`openeu` → :ref:`openeu_tutorial`
* :ref:`esco` → :ref:`esco_tutorial`
* :ref:`competitivedialogue` → :ref:`competitivedialogue_tutorial`
* :ref:`cfaua` → :ref:`cfaua_tutorial`

hasQualificationComplaints is `false`
-------------------------------------

Example tutorials:

* :ref:`belowthreshold` → :ref:`tutorial`
* :ref:`open` → :ref:`open_tutorial`
* :ref:`openua` → :ref:`openua_tutorial`
* :ref:`defense` → :ref:`defense_tutorial`
* :ref:`limited` → :ref:`limited_tutorial`
* :ref:`cfaselectionua` → :ref:`cfaselection_tutorial`
* :ref:`pricequotation` → :ref:`pricequotation_tutorial`
