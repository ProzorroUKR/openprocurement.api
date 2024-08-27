.. _award_complain_duration:

awardComplainDuration
========================

Field `awardComplainDuration` is a integer field that indicates the duration of contesting the results of determining the winne

Possible values for `awardComplainDuration` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/award-complain-duration-values.csv
   :header-rows: 1

awardComplainDuration is `true`
----------------------------------

Let's create a tender `belowThreshold`:

.. http:example:: http/award-complain-duration-tender-post-1.http
   :code:

Then add relatedLot for item:

.. http:example:: http/award-complain-duration-tender-patch-1.http
   :code:

Here we can check that "complaintPeriod" field is absent in the response.
