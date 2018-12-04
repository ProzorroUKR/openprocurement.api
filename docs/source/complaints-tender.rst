.. Kicking page rebuild 2014-10-30 17:00:08

Claim/Complaint Retrieval
=========================

Tender Conditions Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Conditions Claims/Complaints:

.. include:: tutorial/complaints-list.http
   :code:

And check individual complaint or claim:

.. include:: tutorial/complaint.http
   :code:


Claim Submission
================

If tender conditions are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Conditions Claim.

Tender Conditions Claim Submission (with documents)
---------------------------------------------------

At first create a claim:

.. include:: tutorial/complaint-submission.http
   :code:

Then upload necessary documents:

.. include:: tutorial/complaint-submission-upload.http
   :code:

Submit tender conditions claim:

.. include:: tutorial/complaint-claim.http
   :code:

Tender Conditions Claim Submission (without documents)
------------------------------------------------------

Create claim that does not need additional documents:

.. include:: tutorial/complaint-submission-claim.http
   :code:

Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: tutorial/complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: tutorial/complaint-satisfy.http
   :code:


Disagreement with decision
--------------------------

.. include:: tutorial/complaint-escalate.http
   :code:
