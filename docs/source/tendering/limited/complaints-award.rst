

Complaint Retrieval
=========================

Tender Award Complaint Retrieval
-------------------------------------------

You can list all Tender Award Complaints:

.. include:: http/tutorial/award-complaints-list.http
   :code:

And check individual complaint:

.. include:: http/tutorial/award-complaint.http
   :code:

Complaint Submission
====================

If tender award is favoriting certain supplier, or in any other viable case, any registered user can submit Tender Award Complaint.

Tender Award Complaint Submission (with documents)
---------------------------------------------------

At first create a complaint.

.. include:: http/tutorial/award-complaint-submission.http
   :code:

Then upload necessary documents:

.. include:: http/tutorial/award-complaint-submission-upload.http
   :code:

Submit tender award complaint:

.. include:: http/tutorial/award-complaint-complaint.http
   :code:

Tender Award Complaint Submission (without documents)
-----------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: http/tutorial/award-complaint-submission-complaint.http
   :code:

Complaint Resolution
====================

Rejecting Tender Award Complaint
-------------------------------------

.. include:: http/tutorial/award-complaint-reject.http
   :code:


Accepting Tender Award Complaint
-------------------------------------

.. include:: http/tutorial/award-complaint-accept.http
   :code:


Submitting Tender Award Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: http/tutorial/award-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: http/tutorial/award-complaint-resolve.http
   :code:

Or declines it:

.. include:: http/tutorial/award-complaint-decline.http
   :code:

Correcting problems
-------------------

If tender award complaint was satisfied by the Complaint Review Body, then procuring entity has to correct problems.

One of the possible solutions is award cancellation:

.. include:: http/tutorial/award-complaint-satisfied-resolving.http
   :code:

Creating new award:

.. include:: http/tutorial/award-complaint-newaward.http
   :code:

Submitting Resolution Confirmation
----------------------------------

When complaint has been successfully resolved, procuring entity submits resolution confirmation.

.. include:: http/tutorial/award-complaint-resolved.http
   :code:

Submitting complaint to new award
---------------------------------

.. include:: http/tutorial/award-complaint-submit.http
   :code:

Cancelling Tender Award Complaint
=================================

Cancelling not accepted complaint
---------------------------------

.. include:: http/tutorial/award-complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: http/tutorial/award-complaint-accepted-stopping.http
   :code:

.. include:: http/tutorial/award-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: http/tutorial/award-complaint-accepted-stopped.http
   :code:
