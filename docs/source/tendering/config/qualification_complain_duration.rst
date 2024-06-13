.. _qualification_complain_duration:

qualificationComplainDuration
=============================

Field `qualificationComplainDuration` is an integer field that determines the duration of appealing the qualification results.

Possible values for `qualificationComplainDuration` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/qualification-complain-duration-values.csv
   :header-rows: 1

Examples
--------

Let's create a tender with `qualificationComplainDuration` 5 days:

.. http:example:: http/qualification-complain-duration-5-days.http
   :code:

Tender created successfully with expected complaint periods, each of which ends five days after the qualification is created.
