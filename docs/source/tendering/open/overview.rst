Overview
========

The Open Procurement Open procedure is plugin to `Open Procurement API` software.  It requires 0.12 version
of `openprocurement.api package
<https://github.com/ProzorroUKR/openprocurement.api>`_ to work.

REST-ful interface to plugin is in line with core software design principles. 


Main responsibilities
---------------------

Open Procurement Open procedure is dedicated to Open Tender procedure for
Ukrainian above threshold procurements.  The code for that type of procedure
is `aboveThreshold`.

Business logic
--------------

The approach to Open procedure is different from core Open Procurement API
procedure (that is used for below threshold procurements) mainly in
:ref:`stage that precedes <open_tendering>` auction.  Differences are in the
following aspects:

1) Tender can be edited through the whole tenderPeriod (while in
   active.tendering state), but any edit that is close to
   tenderPeriod.endDate would require extending that period.

2) There is no dedicated active.enguiries state. 

3) Questions can be asked within enquiryPeriod that is based upon
   tenderPeriod.

4) Answers are provided during the whole tenderPeriod.

5) Bids can be placed during the whole tenderPeriod.

6) Placed bids are invalidated after any tender condition editing and have to
   be re-confirmed.

Next steps
----------
You might find it helpful to look at the :ref:`open_tutorial`.
