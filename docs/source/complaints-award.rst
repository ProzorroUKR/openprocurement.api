.. Kicking page rebuild 2014-10-30 17:00:08

Claim/Complaint Retrieval
=========================

Tender Award Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Award Claims/Complaints:

.. include:: tutorial/award-complaints-list.http
   :code:

And check individual complaint:

.. include:: tutorial/award-complaint.http
   :code:

Claim Submission
================

If tender award is favoriting certain supplier, or in any other viable case, participants can submit Tender Award Claim.

Tender Award Claim Submission (with documents)
----------------------------------------------

At first create a claim. Send POST request with bidder's access token.

.. include:: tutorial/award-complaint-submission.http
   :code:

Then upload necessary documents:

.. include:: tutorial/award-complaint-submission-upload.http
   :code:

Submit tender award claim:

.. include:: tutorial/award-complaint-claim.http
   :code:

Tender Award Claim Submission (without documents)
-------------------------------------------------

You can submit claim that does not need additional documents:

.. include:: tutorial/award-complaint-submission-claim.http
   :code:


Complaint Submission
====================

If tender award is favoriting certain supplier, or in any other viable case, participants who were admitted to auction can submit Tender Award Complaint.

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

Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: tutorial/award-complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: tutorial/award-complaint-satisfy.http
   :code:


Unsatisfying resolution
-----------------------

.. include:: tutorial/award-complaint-unsatisfy.http
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

If tender award complaint was satisfied by the Complaint Review Body, then procuring entity has to correct problems.

One of the possible solutions is award cancellation:


.. include:: tutorial/award-complaint-satisfied-resolving.http
   :code:

After award cancellation system generates new award. Its location is present in the `Location` header of response.

Submitting Resolution Confirmation
----------------------------------
When complaint has been successfully resolved, procuring entity submits resolution confirmation.

.. include:: tutorial/award-complaint-resolved.http
   :code:

Submitting complaint to new award
---------------------------------

.. include:: tutorial/award-complaint-submit.http
   :code:

Cancelling Tender Award Complaint
=================================

Cancelling not accepted complaint
---------------------------------

.. include:: tutorial/award-complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: tutorial/award-complaint-accepted-stopping.http
   :code:

.. include:: tutorial/award-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: tutorial/award-complaint-accepted-stopped.http
   :code:
