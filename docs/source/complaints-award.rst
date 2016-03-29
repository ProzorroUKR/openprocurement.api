.. Kicking page rebuild 2014-10-30 17:00:08

Complaint Retrieval
=========================

Tender Award Complaint Retrieval
-------------------------------------------

You can list all Tender Award Complaints:

.. include:: tutorial/award-complaints-list.http
   :code:

And check individual complaint:

.. include:: tutorial/award-complaint.http
   :code:

Complaint Submission
====================

If tender award is favoriting certain supplier, or in any other viable case, participants can submit Tender Award Complaint.

Tender Award Complaint Submission (with documents)
---------------------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. include:: tutorial/award-complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: tutorial/award-complaint-submission-upload.http
   :code:

Submit tender award complaint:
   
.. include:: tutorial/award-complaint-complaint.http
   :code:

Tender Award Complaint Submission (without documents)
-----------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: tutorial/award-complaint-submission-complaint.http
   :code:

Complaint Resolution
====================

Rejecting Tender Award Complaint
-------------------------------------

.. include:: tutorial/award-complaint-reject.http
   :code:


Accepting Tender Award Complaint
-------------------------------------

.. include:: tutorial/award-complaint-accept.http
   :code:


Submitting Tender Award Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: tutorial/award-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: tutorial/award-complaint-resolve.http
   :code:

Or declines it:

.. include:: tutorial/award-complaint-decline.http
   :code:

Correcting problems
-------------------

Cancelling award:

.. include:: tutorial/award-complaint-satisfied-resolving.http
   :code:

New generated award location present in Location header.

Submitting Resolution Confirmation
----------------------------------

.. include:: tutorial/award-complaint-resolved.http
   :code:

Submit complaint to new award
-----------------------------

.. include:: tutorial/award-complaint-submit.http
   :code:

Cancelling Tender Award Complaint
=================================

.. include:: tutorial/award-complaint-cancel.http
   :code:
