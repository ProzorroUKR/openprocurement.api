.. _clarification_until_duration:

clarificationUntilDuration
==========================

Field `clarificationUntilDuration` is an integer field that sets the number of days for the customer to respond to the request.

Possible values for `clarificationUntilDuration` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/clarification-until-duration-values.csv
   :header-rows: 1


Examples
--------

Let's create a tender with `clarificationUntilDuration` one work day:

.. http:example:: http/clarification-until-duration-1-working-day.http
   :code:

Tender created successfully with expected clarificationUntil value, which ends one working day after the enquiryPeriod startDate is created.

Let's create a tender with `clarificationUntilDuration` three calendar days:

.. http:example:: http/clarification-until-duration-3-calendar-days.http
   :code:

Tender created successfully with expected clarificationUntil value, which ends three calendar days after the enquiryPeriod startDate is created.

Let's create a tender with `clarificationUntilDuration` three working days:

.. http:example:: http/clarification-until-duration-3-working-days.http
   :code:

Tender created successfully with expected clarificationUntil value, which ends three working days after the enquiryPeriod startDate is created.
