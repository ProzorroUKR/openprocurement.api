

Claim/Complaint Retrieval
=========================

Tender Conditions Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Conditions Claims/Complaints:

.. httpexample:: http/complaints/complaints-list.http
   :code:

And check individual complaint or claim:

.. httpexample:: http/complaints/complaint.http
   :code:

Claim Submission
================

If tender conditions are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Conditions Claim.

Tender Conditions Claim Submission (with documents)
---------------------------------------------------

At first create a claim:

.. httpexample:: http/complaints/claim-submission.http
   :code:

Then upload necessary documents:

.. httpexample:: http/complaints/complaint-submission-upload.http
   :code:

Submit tender conditions claim:

.. httpexample:: http/complaints/complaint-claim.http
   :code:

Tender Conditions Claim Submission (without documents)
------------------------------------------------------

You can submit claim that does not need additional documents:

.. httpexample:: http/complaints/complaint-submission-claim.http
   :code:

Claim's Answer
==============

Answer to resolved claim
------------------------

.. httpexample:: http/complaints/complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. httpexample:: http/complaints/complaint-satisfy.http
   :code:


Escalate claim to complaint
---------------------------

.. httpexample:: http/complaints/complaint-escalate.http
   :code: