.. _frameworks_clarification_until_duration:

clarificationUntilDuration
==========================

Field `clarificationUntilDuration` is the integer field that sets the number of days for the customer to respond to the inquiry.

Possible values for `clarificationUntilDuration` field depends on `frameworkType` field:

.. csv-table::
   :file: csv/clarification-until-duration-values.csv
   :header-rows: 1


Examples
--------

`clarificationsUntil` field calculates during framework creation. For `dynamicPurchasingSystem` type it's 3 working days, as you can see below in `enquiryPeriod`:


.. http:example:: http/restricted/framework-with-agreement.http
   :code:

As you can see, `clarificationsUntil` field is ahead of `endDate` field by 3 working days.