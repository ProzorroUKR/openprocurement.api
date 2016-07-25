.. Kicking page rebuild 2014-10-30 17:00:08

Claim/Complaint Retrieval
=========================

Tender Qualification Claim/Complaint Retrieval
----------------------------------------------

You can list all Tender Qualification Claims/Complaints:

.. include:: tutorial/qualification-complaints-list.http
   :code:

And check individual complaint:

.. include:: tutorial/qualification-complaint.http
   :code:

Claim Submission
================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Claim.

Tender Qualification Claim Submission (with documents)
------------------------------------------------------

At first create a claim. Send POST request with bidder's access token.

.. include:: tutorial/qualification-complaint-submission.http
   :code:

Then upload necessary documents:

.. include:: tutorial/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification claim:

.. include:: tutorial/qualification-complaint-claim.http
   :code:

Tender Qualification Claim Submission (without documents)
---------------------------------------------------------

You can submit claim that does not need additional documents:

.. include:: tutorial/qualification-complaint-submission-claim.http
   :code:


Complaint Submission
====================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Complaint.

Tender Qualification Complaint Submission (with documents)
----------------------------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. include:: tutorial/qualification-complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: tutorial/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification complaint:
   
.. include:: tutorial/qualification-complaint-complaint.http
   :code:

Tender Qualification Complaint Submission (without documents)
-------------------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: tutorial/qualification-complaint-submission-complaint.http
   :code:

Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: tutorial/qualification-complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: tutorial/qualification-complaint-satisfy.http
   :code:


Unsatisfying resolution
-----------------------

.. include:: tutorial/qualification-complaint-unsatisfy.http
   :code:


Complaint Resolution
====================

Rejecting Tender Qualification Complaint
----------------------------------------

.. include:: tutorial/qualification-complaint-reject.http
   :code:


Accepting Tender Qualification Complaint
----------------------------------------

.. include:: tutorial/qualification-complaint-accept.http
   :code:


Submitting Tender Qualification Complaint Resolution
----------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: tutorial/qualification-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: tutorial/qualification-complaint-resolve.http
   :code:

Or declines it:

.. include:: tutorial/qualification-complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. include:: tutorial/qualification-complaint-resolved.http
   :code:

Cancelling Tender Qualification Complaint
=========================================

Cancelling not accepted complaint
---------------------------------

.. include:: tutorial/qualification-complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: tutorial/qualification-complaint-accepted-stopping.http
   :code:

.. include:: tutorial/qualification-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: tutorial/qualification-complaint-accepted-stopped.http
   :code:
