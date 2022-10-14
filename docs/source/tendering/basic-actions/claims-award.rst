

Claim/Complaint Retrieval
=========================

Tender Award Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Award Claims/Complaints:

.. http:example:: http/complaints/award-complaints-list.http
   :code:

And check individual complaint:

.. http:example:: http/complaints/award-complaint.http
   :code:

Claim Submission
================

If tender award is favoriting certain supplier, or in any other viable case, participants can submit Tender Award Claim.

Tender Award Claim Submission (with documents)
----------------------------------------------

At first create a claim. Send POST request with bidder's access token.

.. http:example:: http/complaints/award-complaint-submission.http
   :code:

Then upload necessary documents:

.. http:example:: http/complaints/award-complaint-submission-upload.http
   :code:

Submit tender award claim:

.. http:example:: http/complaints/award-complaint-claim.http
   :code:

Tender Award Claim Submission (without documents)
-------------------------------------------------

You can submit claim that does not need additional documents:

.. http:example:: http/complaints/award-complaint-submission-claim.http
   :code:

Claim's Answer
==============

Answer to resolved claim
------------------------

.. http:example:: http/complaints/award-complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. http:example:: http/complaints/award-complaint-satisfy.http
   :code:


Unsatisfying resolution
-----------------------

.. http:example:: http/complaints/award-complaint-unsatisfy.http
   :code:
