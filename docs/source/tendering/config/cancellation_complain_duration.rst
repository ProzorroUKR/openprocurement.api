.. _cancellation_complain_duration:

cancellationComplainDuration
=============================

Field `cancellationComplainDuration` is a integer field that indicates the duration of contesting the results of determining the winne

Possible values for `cancellationComplainDuration` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/cancellation-complain-duration-values.csv
   :header-rows: 1

cancellationComplainDuration is `true`
--------------------------------------

Let's create a tender `belowThreshold`:

.. http:example:: http/cancellation-complain-duration-tender-post-2.http
   :code:

Then add relatedLot for item:

.. http:example:: http/cancellation-complain-duration-tender-patch-2.http
   :code:

Here we can check that "complaintPeriod" field is absent in the response.

Now, let's create a tender `aboveThreshold`:

.. http:example:: http/cancellation-complain-duration-tender-post-1.http
   :code:

Then add relatedLot for item:

.. http:example:: http/cancellation-complain-duration-tender-patch-1.http
   :code:

We'll see that response contains a "complaintPeriod" field, which means that a complaint period will appear for the tenders with `cancellationComplainDuration` higher than 0