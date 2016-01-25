
.. _tendering:

Tendering
=========

Open UA procedure has `active.tendering` status can be represented with
following diagram:

.. image:: _static/active-tendering.png


Constraints
-----------

 - `tenderPeriod` cannot be shorter then 15 days.

 - `enquiryPeriod` always ends 3 days before tenderPeriod ends.

 - If tender conditions are modified with less then 7 days left to
   `tenderPeriod.endDate`, it has to be extended to meet the contraint.

Claims and Complaits
~~~~~~~~~~~~~~~~~~~~

 - Claims can be submitted only if there is less then 10 or more days left
   in tenderPeriod.

 - Complaints can be submitted only if there is 4 or more days left in
   tenderPeriod.
