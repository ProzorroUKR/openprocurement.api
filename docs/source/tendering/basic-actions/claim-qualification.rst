

Claim/Complaint Retrieval
=========================

Tender Qualification Claim/Complaint Retrieval
----------------------------------------------

You can list all Tender Qualification Claims/Complaints:

.. http:example:: http/complaints/qualification-complaints-list.http
   :code:

And check individual complaint:

.. http:example:: http/complaints/qualification-complaint.http
   :code:

Claim Submission
================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Claim.

Tender Qualification Claim Submission (with documents)
------------------------------------------------------

At first create a claim. Send POST request with bidder's access token.

.. http:example:: http/complaints/qualification-complaint-submission.http
   :code:

Then upload necessary documents:

.. http:example:: http/complaints/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification claim:

.. http:example:: http/complaints/qualification-complaint-claim.http
   :code:

Tender Qualification Claim Submission (without documents)
---------------------------------------------------------

You can submit claim that does not need additional documents:

.. http:example:: http/complaints/qualification-complaint-submission-claim.http
   :code:


Claim's Answer
==============

Answer to resolved claim
------------------------

.. http:example:: http/complaints/qualification-complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. http:example:: http/complaints/qualification-complaint-satisfy.http
   :code:


Unsatisfying resolution
-----------------------

.. http:example:: http/complaints/qualification-complaint-unsatisfy.http
   :code:
