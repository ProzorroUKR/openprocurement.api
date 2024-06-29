
.. _qualification_duration:

qualificationDuration
=====================

Field `qualificationDuration` is an integer field that determines the duration of the participants' qualification period in days.

Possible values for `qualificationDuration` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/qualification-duration-values.csv
   :header-rows: 1

Examples
--------


Let's create a tender with `qualificationDuration` 20 days:

.. http:example:: http/qualification-duration-period-20-days.http
   :code:

Tender created successfully with expected qualification period (20 days in this case).