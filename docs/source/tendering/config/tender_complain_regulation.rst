.. _tender_complain_regulation:

tenderComplainRegulation
===========================

Field `tenderComplainRegulation` is a integer field that determines the final date of the period for contesting the terms of the tender documentation in accordance with the deadline for submitting tender offers.

Possible values for `tenderComplainRegulation` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/tender-complain-regulation-values.csv
   :header-rows: 1

Configuration peculiarities
----------------------------

Let's create a tender `belowThreshold`:

.. http:example:: http/tender-complain-regulation-tender-post-2.http
   :code:

Then add relatedLot for item:

.. http:example:: http/tender-complain-regulation-tender-patch-2.http
   :code:

Here we can check that "complaintPeriod" field is absent in the response.

Now, let's create a tender `aboveThreshold`:

.. http:example:: http/tender-complain-regulation-tender-post-1.http
   :code:

Then add relatedLot for item:

.. http:example:: http/tender-complain-regulation-tender-patch-1.http
   :code:

We'll see that response contains a "complaintPeriod" field, which means that a complaint period will appear for the tenders with `tenderComplainRegulation` higher thatn 0