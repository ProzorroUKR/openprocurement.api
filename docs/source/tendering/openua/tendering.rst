
.. _openua_tendering:

Tendering
=========

Open UA procedure has `active.tendering` status and can be represented with
the following diagram:

.. image:: _static/active-tendering.png


Constraints
-----------

 - `tenderPeriod` cannot be shorter than 15 days.

 - `enquiryPeriod` always ends 10 days before tenderPeriod ends.

 - If tender conditions are modified with less than 7 days left to
   `tenderPeriod.endDate`, this period should be extended so that
   from the moment of the change in the tender documentation until
   `tenderPeriod.endDate` has remained at least 7 days.

Claims and Complaits
~~~~~~~~~~~~~~~~~~~~

 - Claims can be submitted only if there are more than 10 days left
   in tenderPeriod.

 - Complaints can be submitted only if there are 4 or more days left in
   tenderPeriod.
