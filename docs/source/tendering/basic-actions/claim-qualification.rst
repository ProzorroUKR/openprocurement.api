

Claim/Complaint Retrieval
=========================

Tender Qualification Claim/Complaint Retrieval
----------------------------------------------

You can list all Tender Qualification Claims/Complaints:

.. include:: ../http/complaints/qualification-complaints-list.http
   :code:

And check individual complaint:

.. include:: ../http/complaints/qualification-complaint.http
   :code:

Claim Submission
================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Claim.

Tender Qualification Claim Submission (with documents)
------------------------------------------------------

At first create a claim. Send POST request with bidder's access token.

.. include:: ../http/complaints/qualification-complaint-submission.http
   :code:

Then upload necessary documents:

.. include:: ../http/complaints/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification claim:

.. include:: ../http/complaints/qualification-complaint-claim.http
   :code:

Tender Qualification Claim Submission (without documents)
---------------------------------------------------------

You can submit claim that does not need additional documents:

.. include:: ../http/complaints/qualification-complaint-submission-claim.http
   :code:


Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: ../http/complaints/qualification-complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: ../http/complaints/qualification-complaint-satisfy.http
   :code:


Unsatisfying resolution
-----------------------

.. include:: ../http/complaints/qualification-complaint-unsatisfy.http
   :code:
