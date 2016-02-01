.. Kicking page rebuild 2014-10-30 17:00:08

Claim/Complaint Retrieval
=========================

Tender Award Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Award Claims/Complaints:

.. include:: tutorial/award-complaints-list.http
   :code:

And check individual complaint or claim:

.. include:: tutorial/award-complaint.http
   :code:

Complaint Submission
====================

If tender conditions are favoriting only one provider, or in any other viable case, one can submit Tender Award Claim.

Tender Award Complaint Submission (with documents)
---------------------------------------------------

At first create a claim:

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


Accepting Tender Conditions Complaint
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

Submitting Resolution Confirmation
----------------------------------

.. include:: tutorial/award-complaint-resolved.http
   :code:

Cancelling Tender Award Complaint
=================================

.. include:: tutorial/award-complaint-cancel.http
   :code:
